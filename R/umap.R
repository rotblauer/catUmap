library(umap)
library(data.table)
library(optparse)

# parse the command line arguments
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
    default = 100,
    help = "n_neighbors"
  ),
  make_option(
    c("-s", "--select"),
    type = "integer",
    default = 20,
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
    c("-t", "--transform"),
    type = "logical",
    default = TRUE,
    help = "boolean to transform lat lon to xyz"
  )
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

df <- fread(opt$input)


n_neighbor = opt$n_neighbors
select = opt$select
distanceType = opt$distanceType
additionalColumns = strsplit(opt$columnList, ",")[[1]]
columnList = c("lat", "lon")
if (opt$transform) {
  df[, c("x", "y", "z") := list(sin(lat) * cos(lon), sin(lat) * sin(lon), cos(lat))]
  columnList = c("x", "y", "z")
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
    ".txt.gz"
  )

if (file.exists(umapOutput)) {
  print(paste0("file ", umapOutput, " exists"))
} else {
  sub = df[seq(1, nrow(df), select), ]
  subdf = sub[, ..columnList]
  # stop()
  print(paste0("running umap for ", umapOutput))
  
  umapConfig = umap.defaults
  umapConfig$n_neighbors = n_neighbor
  umapConfig$metric = distanceType
  umapConfig$verbose = TRUE
  umapConfig$random_state = 42
  umap = umap(subdf, config = umapConfig)
  
  sub$umap_1 = umap$layout[, 1]
  sub$umap_2 = umap$layout[, 2]
  
  gzOut = gzfile(umapOutput, "w")
  
  write.table(sub,
              gzOut,
              row.names = FALSE,
              quote = FALSE,
              sep = "\t")
  close(gzOut)
}
