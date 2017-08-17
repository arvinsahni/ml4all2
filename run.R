library(shiny)

#port <- Sys.getenv('PORT')
port2=options(shiny.port = 7775)

cat("hello cat")
cat(port2)
cat("done")
shiny::runApp(
  appDir = getwd(),
  host = '127.0.0.0',
  port = as.numeric(port2)
)
