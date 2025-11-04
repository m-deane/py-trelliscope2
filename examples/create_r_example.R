#!/usr/bin/env Rscript

# Set CRAN mirror
options(repos = c(CRAN = "https://cloud.r-project.org"))

# Try to load trelliscope, install from GitHub if needed
if (!require("trelliscope", quietly = TRUE)) {
  cat("Installing trelliscope from GitHub...\n")
  if (!require("remotes", quietly = TRUE)) {
    install.packages("remotes")
  }
  remotes::install_github("trelliscope/trelliscope")
}

library(trelliscope)

# Create minimal example with just 3 panels
cat("Creating minimal R trelliscope example...\n")

# Simple data frame
df <- data.frame(
  id = 1:3,
  category = c("A", "B", "C"),
  value = c(10, 20, 30),
  stringsAsFactors = FALSE
)

# Create simple plot panel column using base R plotting
# We'll save plots as PNG files instead of using ggplot to keep it simple
output_dir <- "examples/output/r_example"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

panels_dir <- file.path(output_dir, "panels")
dir.create(panels_dir, recursive = TRUE, showWarnings = FALSE)

# Generate simple PNG plots
for (i in 1:nrow(df)) {
  png_file <- file.path(panels_dir, paste0(i-1, ".png"))
  png(png_file, width = 400, height = 300)
  plot(df$id[i], df$value[i],
       xlim = c(0, 4), ylim = c(0, 40),
       pch = 19, cex = 3, col = i + 1,
       main = paste("Category", df$category[i]),
       xlab = "ID", ylab = "Value")
  text(df$id[i], df$value[i] + 5, labels = df$category[i], cex = 2)
  dev.off()
  cat("  Created panel", i-1, "\n")
}

# Add panel column as file paths
df$panel <- file.path("panels", paste0(0:2, ".png"))

# Create trelliscope display
cat("Creating trelliscope display...\n")
trdf <- as_trelliscope_df(df, name = "r_example", path = output_dir)

# Write the display
cat("Writing display files...\n")
write_display(trdf, path = output_dir, force_write = TRUE)

cat("\n✓ R example created in:", output_dir, "\n")
cat("  Files created:\n")
files <- list.files(output_dir, recursive = TRUE)
for (f in files) {
  cat("    -", f, "\n")
}

cat("\nNow check the displayInfo.json and metaData files!\n")
