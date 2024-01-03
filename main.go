package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
	"strings"
	"time"

	catnames "github.com/rotblauer/cattracks-names"
	"github.com/tidwall/gjson"
)

type T struct {
	Type     string `json:"type"`
	Id       int    `json:"id"`
	Geometry struct {
		Type        string    `json:"type"`
		Coordinates []float64 `json:"coordinates"`
	} `json:"geometry"`
	Properties struct {
		Accuracy  float64   `json:"Accuracy"`
		Activity  string    `json:"Activity"`
		Elevation float64   `json:"Elevation"`
		Heading   float64   `json:"Heading"`
		Name      string    `json:"Name"`
		Notes     string    `json:"Notes"`
		Pressure  float64   `json:"Pressure"`
		Speed     float64   `json:"Speed"`
		Time      time.Time `json:"Time"`
		UUID      string    `json:"UUID"`
		UnixTime  int       `json:"UnixTime"`
		Version   string    `json:"Version"`
	} `json:"properties"`
}

func passesAccuracy(accuracy float64, requiredAccuracy float64) bool {
	return (accuracy > 0 && accuracy < requiredAccuracy) || requiredAccuracy < 0
}

func validActivity(activity string, require bool, removeUnknownActivity bool) bool {
	return !require || (activity != "" && (!removeUnknownActivity || activity != "Unknown"))
}

func parseStreamPerProperty(reader io.Reader, writer io.Writer, n int, property string, names map[string]bool, accuracy float64, requireActivity bool, removeUnknownActivity bool) {
	dec := json.NewDecoder(reader)
	m := make(map[string]int)
	pCount := 0
	for {
		var t T
		if err := dec.Decode(&t); err == io.EOF {
			break
		} else if err != nil {
			panic(err)
		}
		//	switch on the property to select on
		switch property {
		case "Name":
			t.Properties.Name = catnames.SanitizeName(catnames.AliasOrName(t.Properties.Name))
			// if names is empty or contains the name, increment the count
			if passName(names, t) && passesAccuracy(t.Properties.Accuracy, accuracy) && validActivity(t.Properties.Activity, requireActivity, removeUnknownActivity) {
				m[t.Properties.Name]++
				if m[t.Properties.Name]%n == 0 {
					printT(t, writer)
					pCount++
					if pCount%10000 == 0 {
						printMap(m, os.Stderr)
					}
				}
			}
		default:
			panic("invalid property")
		}
	}
	printMap(m, os.Stderr)
}

func passName(names map[string]bool, t T) bool {
	return len(names) == 0 || names[t.Properties.Name]
}

func printT(t T, w io.Writer) {
	enc := json.NewEncoder(w)
	err := enc.Encode(t)
	if err != nil {
		panic(err)
	}
}

func printMap(m map[string]int, w io.Writer) {
	enc := json.NewEncoder(w)
	err := enc.Encode(m)
	if err != nil {
		panic(err)
	}
}

var flagNumber = flag.Int("n", 100, "select every nth")
var flagProperty = flag.String("p", "Name", "property to select on - select every nth within unique values of this property")
var flagNames = flag.String("names", "", "names to select on")
var flagRequiredAccuracy = flag.Float64("min-accuracy", 100, "minimum accuracy to select on, set to -1 to skip")
var flagRequireActivity = flag.Bool("require-activity", true, "require a valid activity (non-empty)")
var flagRemoveUnknownActivity = flag.Bool("remove-unknown-activity", true, "remove unknown activity")

// example usage:
// cat /tmp/2019-01-*.json | go run main.go -n 100 -p Name -names kk,ia,rye,pr,jr,ric,mat,jlc -min-accuracy 100 -require-activity=true > /tmp/2019-01-uniq.json

func main() {
	flag.Parse()

	// parse the flagNames into a set

	if len(flag.Args()) > 0 && flag.Args()[0] == "filter" {
		filterStream(os.Stdin, os.Stdout, splitFlagStringSlice(*flagMatchAll), splitFlagStringSlice(*flagMatchAny), splitFlagStringSlice(*flagMatchNone))
		return
	}

	names := make(map[string]bool)

	// if the flagNames is not empty, split on comma and add to the set
	if *flagNames != "" {
		for _, name := range regexp.MustCompile(`,`).Split(*flagNames, -1) {
			names[name] = true
		}
	}

	parseStreamPerProperty(os.Stdin, os.Stdout, *flagNumber, *flagProperty, names, *flagRequiredAccuracy, *flagRequireActivity, *flagRemoveUnknownActivity)
}

var flagMatchAll = flag.String("match-all", "", "match all of these properties (gjson syntax, comma separated queries)")
var flagMatchAny = flag.String("match-any", "", "match any of these properties (gjson syntax, comma separated queries)")
var flagMatchNone = flag.String("match-none", "", "match none of these properties (gjson syntax, comma separated queries)")
var errInvalidMatchAll = errors.New("invalid match-all")
var errInvalidMatchAny = errors.New("invalid match-any")
var errInvalidMatchNone = errors.New("invalid match-none")

func filterStream(reader io.Reader, writer io.Writer, matchAll []string, matchAny []string, matchNone []string) {
	breader := bufio.NewReader(reader)
	bwriter := bufio.NewWriter(writer)

readLoop:
	for {
		read, err := breader.ReadBytes('\n')
		if err != nil {
			if errors.Is(err, os.ErrClosed) || errors.Is(err, io.EOF) {
				break
			}
			log.Fatalln(err)
		}
		if err := filter(read, matchAll, matchAny, matchNone); err != nil {
			// log.Println(err)
			continue readLoop
		}
		bwriter.Write(read)
		bwriter.Flush()
	}
}

// filter filters some read line on the matchAll, matchAny, and matchNone queries.
// These queries should be written in GJSON query syntax.
// https://github.com/tidwall/gjson/blob/master/SYNTAX.md
func filter(read []byte, matchAll []string, matchAny []string, matchNone []string) error {

	// Here we hack the line into an array containing only this datapoint.
	// This allows us to use the GJSON query syntax, which is designed for use with arrays, not single objects.
	if !gjson.ParseBytes(read).IsArray() {
		read = []byte(fmt.Sprintf("[%s]", string(read)))
	}

	for _, query := range matchAll {
		if res := gjson.GetBytes(read, query); !res.Exists() {
			return fmt.Errorf("%w: %s", errInvalidMatchAll, query)
		}
	}

	didMatchAny := len(matchAny) == 0
	for _, query := range matchAny {
		if gjson.GetBytes(read, query).Exists() {
			didMatchAny = true
			break
		}
	}
	if !didMatchAny {
		return fmt.Errorf("%w: %s", errInvalidMatchAny, matchAny)
	}

	for _, query := range matchNone {
		if gjson.GetBytes(read, query).Exists() {
			return fmt.Errorf("%w: %s", errInvalidMatchNone, query)
		}
	}
	return nil
}

func splitFlagStringSlice(s string) []string {
	if s == "" {
		return []string{}
	}
	return strings.Split(s, ",")
}
