library(ggplot2)
library(readr)
library(tidyr)

data <- read_csv("data.csv") |>
  pivot_longer(!"num graphs", names_to = "processes", values_to = "seconds")

data$processes[data$processes == "serial time"] = 1
data$processes[data$processes == "parallel time"] = 16

p <- ggplot(
  data = data,
  mapping = aes(
    x = `num graphs`,
    y = seconds,
    color = processes,
    shape = processes
  )
) +
  geom_line() +
  geom_point() +
  theme_light()

ggsave("speedup.png", p, width = 8, height = 4, units = "in")
