library(shiny)

#port <- Sys.getenv('PORT')
options(shiny.port = 7775)

cat("hello cat")
cat(port)
cat("done")
shiny::runApp(
  appDir = getwd(),
  host = '0.0.0.0',
  port = as.numeric(port)
)
