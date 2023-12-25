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
else
    echo "File $trimTracksOut already exists"
    
fi

# run main.py on the trimTracksOut file

cat $trimTracksOut \
|zcat \
|.venv/bin/python main.py --metrics "euclidean" "haversine" --output "output/umap.tsv.gz" --components $components --outputRaw "output/raw.tsv.gz"
