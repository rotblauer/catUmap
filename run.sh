#!/bin/bash

# if the first argument is undefined, set it to a default value
masterjson=${1:-"/Volumes/SandCat/tdata/master.json.gz"}
trimTracksOut=${2:-"output/output.json.gz"}
components=${3:-"2"}


# if the trimTracksOut file does not exist, create it
if [ ! -f "$trimTracksOut" ]; then
    cat $masterjson \
    |zcat \
    |go run main.go  -names "rye,ia" \
    |gzip  > $trimTracksOut

# https://github.com/tidwall/gjson/blob/master/SYNTAX.md
#
#   zcat $masterjson \
#   |catnames-cli modify --name-attribute 'properties.Name' --sanitize true \
#   |go run main.go \
#     filter \
#     --match-all 'properties.Accuracy<100' \
#     --match-any 'properties.Name=="ia",properties.Name=="rye"' \
#     --match-none 'properties.Activity=="",properties.Activity=="unknown"' \
#   |gzip  > $trimTracksOut

else
    echo "File $trimTracksOut already exists"

fi

# run main.py on the trimTracksOut file

metrics=("euclidean" "haversine")
for metric in "${metrics[@]}"
do
  
    echo "Metric: $metric"
    cat $trimTracksOut \
    |zcat \
    |.venv/bin/python main.py --metric $metric --output output/$metric.$components.umap.gz --components $components

done



