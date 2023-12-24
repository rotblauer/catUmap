package main

import (
	"encoding/json"
	"flag"
	"io"
	"os"
	"regexp"
	"time"
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

// https://github.com/rotblauer/cattracks-split-cats-uniqcell-gz/blob/4e8d1addce091552ac74466873fe4a719605d6af/main.go#L55C1-L66C2
var aliases = map[*regexp.Regexp]string{
	regexp.MustCompile(`(?i)(Rye.*|Kitty.*|jl)`):                          "rye",
	regexp.MustCompile(`(?i)(.*Papa.*|P2|Isaac.*|.*moto.*|iha|ubp52)`):    "ia",
	regexp.MustCompile(`(?i)(Big.*Ma.*)`):                                 "jr",
	regexp.MustCompile(`(?i)Kayleigh.*`):                                  "kd",
	regexp.MustCompile(`(?i)(KK.*|kek)`):                                  "kk",
	regexp.MustCompile(`(?i)Bob.*`):                                       "rj",
	regexp.MustCompile(`(?i)(Pam.*|Rathbone.*)`):                          "pr",
	regexp.MustCompile(`(?i)(Ric|.*A3_Pixel_XL.*|.*marlin-Pixel-222d.*)`): "ric",
	regexp.MustCompile(`(?i)Twenty7.*`):                                   "mat",
	regexp.MustCompile(`(?i)(.*Carlomag.*|JLC|jlc)`):                      "jlc",
}

func parseName(name string) string {
	for k, v := range aliases {
		if k.MatchString(name) {
			return v
		}
	}
	return name
}

func passesAccuracy(accuracy float64, requiredAccuracy float64) bool {
	return (accuracy > 0 && accuracy < requiredAccuracy) || requiredAccuracy < 0
}

func validActivity(activity string, require bool) bool {
	return !require || activity != ""
}

func parseStreamPerProperty(reader io.Reader, writer io.Writer, n int, property string, names map[string]bool, accuracy float64, requireActivity bool) {
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
			t.Properties.Name = parseName(t.Properties.Name)
			//if names is empty or contains the name, increment the count
			if passName(names, t) && passesAccuracy(t.Properties.Accuracy, accuracy) && validActivity(t.Properties.Activity, requireActivity) {
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

//example usage:
//cat /tmp/2019-01-*.json | go run main.go -n 100 -p Name -names kk,ia,rye,pr,jr,ric,mat,jlc -min-accuracy 100 -require-activity=true > /tmp/2019-01-uniq.json

func main() {
	flag.Parse()
	//parse the flagNames into a set

	names := make(map[string]bool)

	//if the flagNames is not empty, split on comma and add to the set
	if *flagNames != "" {
		for _, name := range regexp.MustCompile(`,`).Split(*flagNames, -1) {
			names[name] = true
		}
	}

	parseStreamPerProperty(os.Stdin, os.Stdout, *flagNumber, *flagProperty, names, *flagRequiredAccuracy, *flagRequireActivity)
}
