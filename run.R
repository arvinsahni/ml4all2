library(shiny)

port <- Sys.getenv('PORT')

cat("hello cat")
cat(port)
cat("done")
shiny::runApp(
  appDir = getwd(),
  host = '0.0.0.0',
  port = as.numeric(port)
)
