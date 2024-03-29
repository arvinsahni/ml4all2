#!/usr/bin/env Rscript
library(shiny)
library(dplyr)
library(DT)
library(plotly)

args<-commandArgs(TRUE)
'%!in%' <- function(x,y)!('%in%'(x,y))

#Source custom plotting functions
source("app/shiny/utils/data.type.R")

#Load datasets from input args
df_train<-read.csv(paste0("app/uploads/",args[1]))
df_test<-read.csv(paste0("app/uploads/",args[2]))

#Check response variable
if (length(names(df_train)[names(df_train) %!in% names(df_test)])==1){
  outcome.var<-names(df_train)[names(df_train) %!in% names(df_test)]
}else if (length(names(df_train)[names(df_train) %!in% names(df_test)])>1){
  print("More than one response variable detected.")
}else{
  print("No response variable detected.")
}

#Put outcome column first
df_train <- df_train %>%
  dplyr::select(get(outcome.var), everything())

#Get data types
target.type<-c("Continuous", "Categorical")
type<-sapply(df_train, data.type)
df_type<-data.frame(type)
df_type$var<-row.names(df_type)
row.names(df_type)<-NULL
print(df_type)
target.vars<-df_type$var[df_type$type %in% target.type]

port1 <- Sys.getenv('PORT')

#shiny::runApp(
  #appDir = getwd(),
  #host = '0.0.0.0',
  #port = as.numeric(port)
#)
cat("in shiny.R")
print("in shiny.R print")
shiny::runApp(appDir="app/", port = 7775)
