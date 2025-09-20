#!/bin/bash

suffixes=(".gzSpeed" ".gzActivity" "gzActivity_facet" ".gzActivity_Name_facet")

parallel -j 4 "find ../output/ -name \"*{}.jpg\" | sort -t_ -k2 -n >  ../output/umap_files{}.txt" ::: ${suffixes[@]}
parallel -j 4 "magick convert -quality 85%  -delay 20 -loop 0 @\"../output/umap_files{}.txt\" ../output/umap{}.gif" ::: ${suffixes[@]}