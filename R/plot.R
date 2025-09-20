library(optparse)
library(data.table)
library(plotly)
library(sf)
library(knitr)
library(rworldmap)

option_list = list(
  make_option(
    c("-i", "--input"),
    type = "character",
    default = "../output/umap_25_10_euclidean.cluster_x_y_z_Speed.tf_TRUE.scale_Speed.embed_fullTRUE.hnsw.txt.gz",
    help = "input file"
  ),
  make_option(
    c("-a", "--alpha"),
    type = "numeric",
    default = 0.01,
    help = "alpha"
  ),
  make_option(
    c("-w", "--width"),
    type = "numeric",
    default = 9,
    help = "width"
  ),
  make_option(
    c("-e", "--height"),
    type = "numeric",
    default = 7,
    help = "height"
  ),
  make_option(
    c("-p", "--pointSize"),
    type = "numeric",
    default = 0.25,
    help = "point size"
  ),
  make_option(
    c("-d", "--dpi"),
    type = "numeric",
    default = 300,
    help = "point size"
  ),
)


opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)
myColor <- rev(RColorBrewer::brewer.pal(11, "Spectral"))
myColor_scale_fill <- scale_fill_gradientn(colours = myColor)
myPalette <-
  colorRampPalette(rev(RColorBrewer::brewer.pal(11, "Spectral")))

colors = myPalette(150)


theme_set(theme_bw(14))

dfWithIndicesCache = paste0(opt$input, "indices.RData")
if (!file.exists(dfWithIndicesCache)) {
  df <- fread(opt$input)
  countriesSP <- getMap(resolution = 'low')
  pointsSP = SpatialPoints(df[, c("lon", "lat")], proj4string = CRS(proj4string(countriesSP)))
  indices = over(pointsSP, countriesSP)
  df = cbind(df, indices)
  # save(df, file = dfWithIndicesCache)
  if (!file.exists("../output/cb_2020_us_county_500k.shp")) {
    url = 'https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_500k.zip'
    download.file(url, destfile = "../output/cb_2020_us_county_500k.zip")
    unzip("../output/cb_2020_us_county_500k.zip", exdir = "../output/")
    
  }
  shape <- read_sf("../output/cb_2020_us_county_500k.shp")
  dfc = df[, c("lon", "lat")]
  coordinates(dfc) <- c("lon", "lat")
  proj4string(dfc) <- CRS("+init=epsg:4269")
  dfc <- st_as_sf(dfc)
  indices = st_join(dfc, shape)
  df = cbind(df, indices)
  save(df, file = dfWithIndicesCache)
}
load(dfWithIndicesCache)
df$NAME = NULL
size <- 0.01
alpha = 0.25

p <-
  ggplot(df, aes(x = umap_2, y = umap_1, color = Speed)) +
  geom_point(alpha = alpha, size = size) +
  scale_color_gradientn(colors = colors) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size = 3))) +
  ggtitle(paste0("Speed - ", gsub(".hnsw.txt.gz", "", basename(opt$input))))

out = paste0(opt$input, "Speed.jpg")
if (!file.exists(out)) {
  ggsave(
    out,
    p,
    width = opt$width,
    height = opt$height,
    dpi = opt$dpi,
  )
}

p <-
  ggplot(df, aes(x = umap_2, y = umap_1, color = Activity)) +
  geom_point(alpha = alpha, size = size) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size = 3)))

out = paste0(opt$input, "Activity.jpg")
if (!file.exists(out)) {
  ggsave(
    out,
    p,
    width = opt$width,
    height = opt$height,
    dpi = opt$dpi,
  )
}
out = paste0(opt$input, "Activity_facet.jpg")
if (!file.exists(out)) {
  ggsave(
    out,
    p + facet_wrap( ~ Activity),
    width = opt$width,
    height = opt$height,
    dpi = opt$dpi,
  )
}

out = paste0(opt$input, "Activity_Name_facet.jpg")
if (!file.exists(out)) {
  ggsave(
    out,
    p + facet_wrap(~ Name),
    width = opt$width,
    height = opt$height,
    dpi = opt$dpi,
  )
}
