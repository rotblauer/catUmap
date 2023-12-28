#!/bin/bash

# if the first argument is undefined, set it to a default value
masterjson=${1:-"/Volumes/SandCat/tdata/master.json.gz"}
trimTracksOut=${2:-"output/output.json.gz"}
components=${3:-"2"}
n_neighbors=${4:-"50"}



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
# use awk to select every 10th line

# | awk 'NR % 10 == 0' \

cat $trimTracksOut \
|zcat \
|.venv/bin/python main.py \
--n_neighbors $n_neighbors \
--metrics "euclidean" "haversine" \
--output "output/$n_neighbors.$components.umap.tsv.gz" \
--components $components \
--outputRaw "output/raw.tsv.gz"
