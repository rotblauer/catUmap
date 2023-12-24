#!/bin/bash

# if the first argument is undefined, set it to a default value
masterjson=${1:-"/Volumes/SandCat/tdata/master.json.gz"}
trimTracksOut=${2:-"output/output.json.gz"}


# if the trimTracksOut file does not exist, create it
if [ ! -f "$trimTracksOut" ]; then
    cat $masterjson \
    |zcat \
    |go run main.go \
    |gzip  > $trimTracksOut
else
	echo "File $trimTracksOut already exists"

fi

# run main.py on the trimTracksOut file

cat $trimTracksOut \
|zcat \
| head -n 500 \
|python3 main.py


