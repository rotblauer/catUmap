#!/bin/bash

seq 5 5 150 | parallel -j 1 "Rscript ../R/umap.R  --n_neighbors {}"