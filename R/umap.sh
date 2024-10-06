#!/bin/bash

seq 5 5 150 | parallel -j 1 "Rscript umap.R  --n_neighbors {}"