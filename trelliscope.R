# R Trelliscope Example - to understand the output structure
# This will help us see what files R generates and their exact format

library(trelliscopejs)
library(ggplot2)
library(dplyr)

# Load the data
data <- read.csv("_data/refinery_margins.csv")

# Convert date to Date type
data$date <- as.Date(data$date)

# Create trelliscope display
plot_output <- data %>%
  ggplot(aes(x = date, y = refinery_kbd)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Refinery Capacity",
    y = "Refinery (kbd)"
  ) +
  facet_trelliscope(
    ~ country,
    name = "refinery_by_country",
    path = "./examples/output/r_example",
    nrow = 2,
    ncol = 3,
    as_plotly = T
  )

# Create trelliscope display
plot_output <- data %>%
  ggplot(aes(x = date, y = refinery_kbd)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Refinery Capacity",
    y = "Refinery (kbd)"
  ) +
  facet_trelliscope(
    ~ country,
    name = "refinery_by_country",
    path = "./examples/output/r_example_static",
    nrow = 2,
    ncol = 3
  )

# View the display
plot_output

# After running, examine the generated files to compare with our Python output
cat("\n=== Generated Files ===\n")
list.files(
  "./examples/output/r_example",
  recursive = TRUE,
  full.names = TRUE
)
