library(uwot)
library(data.table)
library(optparse)
library(rnndescent)

# parse the command line arguments
setwd("~/git/catUmap/scripts/")
option_list = list(
  make_option(
    c("-i", "--input"),
    type = "character",
    default = "../output/raw.tsv.gz",
    help = "input file"
  ),
  make_option(
    c("-n", "--n_neighbors"),
    type = "integer",
    default = 70,
    help = "n_neighbors"
  ),
  make_option(
    c("-s", "--select"),
    type = "integer",
    default = 10,
    help = "select"
  ),
  make_option(
    c("-d", "--distanceType"),
    type = "character",
    default = "euclidean",
    help = "distanceType"
  ),
  make_option(
    c("-c", "--columnList"),
    type = "character",
    default = "Speed",
    help = "columns to cluster in addition to lat,lon"
  ),
  make_option(
    c("-l", "--scaleCols"),
    type = "character",
    default = "Speed",
    help = "columns to scale in addition to lat,lon"
  ),
  make_option(
    c("-t", "--transform"),
    type = "logical",
    default = TRUE,
    help = "boolean to transform lat lon to xyz"
  ),
  make_option(
    c("-e", "--embed"),
    type = "logical",
    default = TRUE,
    help = "embed the full dataset if select is greater than 1"
  ),
  make_option(
    c("--threads"),
    type = "numeric",
    default = 8,
    help = "number of threads to use for umap2"
  )
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

df <- fread(opt$input)
n_neighbor = opt$n_neighbors
select = opt$select
distanceType = opt$distanceType
additionalColumns = strsplit(opt$columnList, ",")[[1]]
scaleCols = strsplit(opt$scaleCols, ",")[[1]]

columnList = c("lat", "lon")

if (opt$transform) {
  deg2rad <- pi / 180
  df[, lat_rad := lat * deg2rad]
  df[, lon_rad := lon * deg2rad]
  df[, c("x", "y", "z") := list(cos(lat_rad) * cos(lon_rad),
                                cos(lat_rad) * sin(lon_rad),
                                sin(lat_rad))]
  # clean up intermediate if you want
  df[, c("lat_rad", "lon_rad") := NULL]
  # df[, c("x", "y", "z") := list(cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat))]
  columnList = c("x", "y", "z")
}

stop()
df$speedOrig = df$Speed
for (col in c(scaleCols, columnList)) {
  print(paste0("scaling ", col))
  df[[col]] = scale(df[[col]])
}


columnList = c(columnList, additionalColumns)
print(paste0("clustering on ", paste0(columnList, collapse = ",")))

umapOutput <-
  paste0(
    "../output/umap_",
    n_neighbor,
    "_",
    select,
    "_",
    distanceType,
    ".cluster_",
    paste0(columnList, collapse = "_"),
    ".tf_",
    opt$transform,
    ".scale_",
    paste0(scaleCols, collapse = "_"),
    ".embed_full",
    opt$embed,
    ".hnsw.v2.txt.gz"
  )

if (file.exists(umapOutput)) {
  print(paste0("file ", umapOutput, " exists"))
} else {
  sub = df[seq(1, nrow(df), select), ]
  subdf = sub[, ..columnList]
  print(paste0("running umap for ", umapOutput))
  umap = umap2(
    X = subdf,
    n_neighbors = n_neighbor,
    metric = distanceType,
    n_components = 2,
    seed = 42,
    verbose = TRUE,
    n_threads = opt$threads,
    nn_method = "nndescent",
    ret_model = opt$embed
  )
  if (opt$embed) {
    print("embedding to full dataset")
    umap =  umap_transform(df[, ..columnList],
                           umap,
                           n_threads = opt$threads,
                           verbose = TRUE)
    sub = df
  }
  
  sub$umap_1 = umap[, 1]
  sub$umap_2 = umap[, 2]
  
  
  gzOut = gzfile(umapOutput, "w")
  
  write.table(sub,
              gzOut,
              row.names = FALSE,
              quote = FALSE,
              sep = "\t")
  close(gzOut)
}
