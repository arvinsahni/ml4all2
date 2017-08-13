SplitColType<-function (data) 
{
  ggplot(mtcars, aes(mpg)) +
    geom_density(alpha = 0.1)
}

cont.density<-function (data, plot.color="coral1", ...) {
    if (!is.data.table(data)) {
      data <- data.table(data)
    }
    if (SplitColType(data)$num_continuous == 0) 
      stop("No Continuous Features")
    continuous <- SplitColType(data)$continuous
    n <- nrow(continuous)
    p <- ncol(continuous)
    pages <- ceiling(p/16)
    for (pg in 1:pages) {
      subset_data <- continuous[, (16 * pg - 15):min(p, 16 * 
                                                       pg), with = FALSE]
      plot <- lapply(seq_along(subset_data), function(j) {
        x <- na.omit(subset_data[, j, with = FALSE])
        ggplot(x, aes_string(x = names(x))) + geom_density(fill = plot.color, 
                                                           alpha = 0.4, ...) + ylab("Density")
      })
      if (pages > 1) {
        suppressWarnings(do.call(grid.arrange, c(plot, ncol = 4, 
                                                 nrow = 4)))
      }
      else {
        suppressWarnings(do.call(grid.arrange, plot))
      }
    }
}