#!/usr/bin/env Rscript
library(data.table)
library(ggplot2)
library(optparse)
library(RColorBrewer)
library(gridExtra)

# Parse command line arguments
option_list = list(
  make_option(
    c("-i", "--input"),
    type = "character",
    default = "../output/test_all_methods.tsv.gz",
    help = "input file with dimensionality reduction results"
  ),
  make_option(
    c("-o", "--output"),
    type = "character",
    default = "../output/dim_reduction_plots.png",
    help = "output plot file"
  ),
  make_option(
    c("-m", "--methods"),
    type = "character",
    default = "pca,svd,ica,tsne",
    help = "comma-separated list of methods to plot"
  ),
  make_option(
    c("-c", "--color_by"),
    type = "character",
    default = "Activity",
    help = "column to use for coloring points"
  ),
  make_option(
    c("-a", "--alpha"),
    type = "numeric",
    default = 0.6,
    help = "point transparency"
  ),
  make_option(
    c("-s", "--point_size"),
    type = "numeric",
    default = 0.8,
    help = "point size"
  ),
  make_option(
    c("-w", "--width"),
    type = "numeric",
    default = 16,
    help = "plot width in inches"
  ),
  make_option(
    c("-h", "--height"),
    type = "numeric",
    default = 12,
    help = "plot height in inches"
  )
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

# Load data
cat("Loading data from:", opt$input, "\n")
df <- fread(opt$input)
cat("Loaded", nrow(df), "rows and", ncol(df), "columns\n")
cat("Columns:", paste(colnames(df), collapse = ", "), "\n")

# Parse methods
methods <- strsplit(opt$methods, ",")[[1]]
methods <- trimws(methods)

# Color palette
colors <- brewer.pal(min(11, length(unique(df[[opt$color_by]]))), "Spectral")

# Create plots for each method
plots <- list()

for (method in methods) {
  x_col <- paste0(method, "_0")
  y_col <- paste0(method, "_1")
  
  if (x_col %in% colnames(df) && y_col %in% colnames(df)) {
    cat("Creating plot for", method, "\n")
    
    p <- ggplot(df, aes_string(x = x_col, y = y_col, color = opt$color_by)) +
      geom_point(alpha = opt$alpha, size = opt$point_size) +
      scale_color_manual(values = colors) +
      theme_minimal() +
      theme(
        legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
        axis.title = element_text(size = 12),
        legend.title = element_text(size = 11),
        legend.text = element_text(size = 10)
      ) +
      labs(
        title = paste(toupper(method), "Dimensionality Reduction"),
        x = paste(toupper(method), "Component 1"),
        y = paste(toupper(method), "Component 2"),
        color = opt$color_by
      ) +
      guides(color = guide_legend(override.aes = list(alpha = 1, size = 3)))
    
    plots[[method]] <- p
  } else {
    cat("Warning: Columns", x_col, "and/or", y_col, "not found for method", method, "\n")
  }
}

# Create combined plot
if (length(plots) > 0) {
  cat("Creating combined plot with", length(plots), "methods\n")
  
  # Arrange plots in a grid
  if (length(plots) == 1) {
    combined_plot <- plots[[1]]
  } else if (length(plots) == 2) {
    combined_plot <- grid.arrange(plots[[1]], plots[[2]], ncol = 2)
  } else if (length(plots) <= 4) {
    combined_plot <- grid.arrange(grobs = plots, ncol = 2)
  } else {
    combined_plot <- grid.arrange(grobs = plots, ncol = 3)
  }
  
  # Save plot
  cat("Saving plot to:", opt$output, "\n")
  ggsave(opt$output, combined_plot, width = opt$width, height = opt$height, dpi = 300)
  
  cat("Plot saved successfully!\n")
} else {
  cat("Error: No valid methods found to plot\n")
  quit(status = 1)
}

# Print summary statistics
cat("\n=== Summary Statistics ===\n")
for (method in methods) {
  x_col <- paste0(method, "_0")
  y_col <- paste0(method, "_1")
  
  if (x_col %in% colnames(df) && y_col %in% colnames(df)) {
    cat(sprintf("%s - Component 1: mean=%.3f, sd=%.3f\n", 
                toupper(method), mean(df[[x_col]], na.rm = TRUE), sd(df[[x_col]], na.rm = TRUE)))
    cat(sprintf("%s - Component 2: mean=%.3f, sd=%.3f\n", 
                toupper(method), mean(df[[y_col]], na.rm = TRUE), sd(df[[y_col]], na.rm = TRUE)))
  }
}

# If clustering results are available, show cluster summary
if ("kmeans_cluster" %in% colnames(df)) {
  cat("\n=== K-means Clustering Summary ===\n")
  cluster_counts <- table(df$kmeans_cluster)
  for (i in names(cluster_counts)) {
    cat(sprintf("Cluster %s: %d points (%.1f%%)\n", 
                i, cluster_counts[i], 100 * cluster_counts[i] / nrow(df)))
  }
}

cat("\nDone!\n")