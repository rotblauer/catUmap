#!/bin/bash

suffixes=(".gzSpeed" ".gzActivity" "gzActivity_facet" ".gzActivity_Name_facet")

parallel -j 4 "find ../output/ -name \"*{}.jpg\" | sort -t_ -k2 -n >  ../output/umap_files{}.txt" ::: ${suffixes[@]}
parallel -j 4 "magick convert -quality 85%  -delay 20 -loop 0 @\"../output/umap_files{}.txt\" ../output/umap{}.gif" ::: ${suffixes[@]}



# for suffix in ${suffixes[@]}; do
# 	find ../output/ -name "*$suffix.jpg" | sort -t_ -k2 -n >  ../output/umap_files$suffix.txt
# 	magick convert -delay 20 -loop 0 @"../output/umap_files$suffix.txt" ../output/umap$suffix.gif
# done

# # 

# find ../output/ -name "*.gzSpeed.jpg" | sort_by_number >  ../output/umap_speed_files.txt


# magick convert -delay 20 -loop 0 @"../output/umap_speed_files.txt" ../output/umap_speed.gif
