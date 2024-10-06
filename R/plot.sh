#!/bin/bash
find ../output/ -name "*.hnsw.txt.gz" | parallel -j 4 "Rscript plot.R --input {}"

