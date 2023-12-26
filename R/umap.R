library(umap)
library(data.table)
library(optparse)

# parse the command line arguments

df <- fread("../output/raw.tsv.gz")


n_neighbors = c(100)
select = 50
distanceTypes = c("euclidean")
columnLists = list(base = sort(c("lat", "lon")),
                   withSpeed = sort(c("lat", "lon", "speed")))

subdf = df[seq(1, nrow(df), select), ]

save(subdf, file = "../output/subdf.RData")

for (columnList in columnLists) {
  for (n_neighbor in n_neighbors) {
    for (distanceType in distanceTypes) {
      umapRdataFile <-
        paste0(
          "../output/umap_",
          n_neighbor,
          "_",
          select,
          "_",
          distanceType,
          paste0(columnList, collapse = "_"),
          ".RData"
        )
      
      if (file.exists(umapRdataFile)) {
        print("skipping")
      } else {
        print(paste0("running umap for ", umapRdataFile))
        umapConfig = umap.defaults
        umapConfig$n_neighbors = n_neighbor
        umapConfig$metric = distanceType
        umapConfig$verbose = TRUE
        umapConfig$random_state = 42
        # run umap on the lat lon columns of the df
        umap = umap(subdf,
                    config = umapConfig)
        # save the umap object
        save(umap, file = umapRdataFile)
      }
    }
  }
}
