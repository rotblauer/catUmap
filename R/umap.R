library(umap)
library(data.table)

df <- fread("../output/raw.tsv.gz")


# if the umap.RData file exists, load it

n_neighbors = c(100)
selectEvery = c(10)
distanceTypes = c("euclidean", "haversine")
columnLists = list(base = sort(c("lat", "lon")),
                   withSpeed = sort(c("lat", "lon", "speed")))

for (columnList in columnLists) {
  for (n_neighbor in n_neighbors) {
    for (select in selectEvery) {
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
          load(umapRdataFile)
        } else {
          subdf = df[seq(1, nrow(df), select), ]
          umapConfig=umap.defaults
          umapConfig$n_neighbors=n_neighbor
          umapConfig$metric=distanceType
          umapConfig$verbose=TRUE
          
          # run umap on the lat lon columns of the df
          umap = umap(
            subdf[, columnList],
            config = umapConfig
          )
          # save the umap object
          save(umap, file = umapRdataFile)
        }
      }
    }
  }
}
