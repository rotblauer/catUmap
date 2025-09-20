#!/bin/bash

# if the first argument is undefined, set it to a default value
masterjson=${1:-"$HOME/tdata/master.json.gz"}
trimTracksOut=${2:-"output/output.json.gz"}
components=${3:-"2"}
n_neighbors=${4:-"50"}
n_epochs=${5:-"200"}

# if catnames-cli is on the PATH, use it otherwise use the full path
  

# if the trimTracksOut file does not exist, create it
if [ ! -f "$trimTracksOut" ]; then

# 👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍 
# https://github.com/tidwall/gjson/blob/master/SYNTAX.md 👍 👍 👍 👍 👍 👍
# 👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍👍 👍 👍 👍 👍 👍
# catnames-cli: https://github.com/rotblauer/cattracks-names
# mac not like zcat zcat, need cat zcat
  cat $masterjson|zcat \
  |catnames-cli modify --name-attribute 'properties.Name' --sanitize true \
  |go run main.go \
    --match-all '#(properties.Speed<50),#(properties.Accuracy<10),#(properties.Activity!="")' \
    --match-any '#(properties.Name=="ia"),#(properties.Name=="rye")' \
    filter \
    |gzip  > $trimTracksOut
    # ,#(properties.Activity!="unknown")
    
else
    echo "File $trimTracksOut already exists"
    
fi

# run main.py on the trimTracksOut file
# use awk to select every 10th line

# | awk 'NR % 10 == 0' \
# --metrics "euclidean" "haversine" \

cat $trimTracksOut \
|zcat \
| awk 'NR % 10 == 0' \
|.venv/bin/python main.py \
--n_neighbors $n_neighbors \
--metrics "none" \
--output "output/$n_neighbors.$components.umap.tsv.gz" \
--components $components \
--outputRaw "output/raw.tsv.gz" \
--n_epochs $n_epochs \
--n_neighbors $n_neighbors \
--standardize
