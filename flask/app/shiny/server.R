function(input, output) {
  output$dtrain <- DT::renderDataTable(
    DT::datatable(df_train[, input$show_vars_dtrain, drop = FALSE], options = list(pageLength = 25)) %>%
      formatStyle(outcome.var, backgroundColor='#D5FDD5')
  )
  
  output$dtest <- DT::renderDataTable(
    DT::datatable(df_test[, input$show_vars_dtest, drop = FALSE], options = list(pageLength = 25))
  )
  
  output$summary.plot.train <- renderPlotly({
    if(class(df_train[,input$show_vars])=="integer" | class(df_train[,input$show_vars])=="numeric"){
      p<-ggplot(df_train, aes_string(input$show_vars))
      p<-p+geom_density(alpha = 0.4, fill="cornflowerblue")
      #p<-p+labs(title = paste("Density plot of", input$show_vars))
      p<-p+theme(axis.title.x=element_blank())
      ggplotly(p)
    }else{
      p<-ggplot(df_train, aes_string(input$show_vars))
      p<-p+geom_bar(fill="#FF8E77")
      #p<-p+labs(title = paste("Bar chart of", input$show_vars))
      p<-p+theme(axis.title.x=element_blank())
      ggplotly(p)
    }
  })
  
  output$summary.plot.test <- renderPlotly({
    if(class(df_test[,input$show_vars])=="integer" | class(df_test[,input$show_vars])=="numeric"){
      p<-ggplot(df_test, aes_string(input$show_vars))
      p<-p+geom_density(alpha = 0.4, fill="cornflowerblue")
      #p<-p+labs(title = paste("Density plot of", input$show_vars))
      p<-p+theme(axis.title.x=element_blank())
      ggplotly(p)
    }else{
      p<-ggplot(df_test, aes_string(input$show_vars))
      p<-p+geom_bar(fill="#C1D4F7")
      #p<-p+labs(title = paste("Bar chart of", input$show_vars))
      p<-p+theme(axis.title.x=element_blank())
      ggplotly(p)
    }
  })
  
  output$summary.table.train <- renderTable({
      raw.table.train<-data.frame(summary(df_train[,input$show_vars, drop = FALSE]))
      summary.table.train<-stringr::str_split_fixed(raw.table.train[,3], ":", 2)
      summary.table.train
  }, colnames = FALSE)

  output$summary.table.test <- renderTable({
    raw.table.test<-data.frame(summary(df_test[,input$show_vars, drop = FALSE]))
    summary.table.test<-stringr::str_split_fixed(raw.table.test[,3], ":", 2)
    summary.table.test
  }, colnames = FALSE)
  
  output$miss.plot <- renderPlot({
    miss.plot(df_train)
  })

  output$miss.table <- renderTable({
    miss.table(df_train)
  })
  
  
  output$relation.plot <- renderPlotly({
    if( data.type(df_train[,input$show_vars2])=="Continuous" & data.type(df_train[,outcome.var])=="Continuous" ){
      p<-ggplot(df_train, aes_string(input$show_vars2, outcome.var))
      p<-p+geom_point(color="#C1D4F7")
      p<-p+geom_smooth(method="loess")
      p<-p+labs(title = paste("Scatter plot of", outcome.var, "vs.", input$show_vars2), x=input$show_vars2, y=outcome.var)
      ggplotly(p)
    }else if(data.type(df_train[,input$show_vars2])=="Categorical" & data.type(df_train[,outcome.var])=="Continuous"){
      p<-ggplot(df_train,aes(as.factor(get(input$show_vars2)), get(outcome.var)))
      p<-p+geom_boxplot(fill="#C1D4F7")
      p<-p+labs(title = paste("Boxplot of", outcome.var, "vs.", input$show_vars2), x=input$show_vars2, y=outcome.var)
      ggplotly(p)
    }else if(data.type(df_train[,input$show_vars2])=="Continuous" & data.type(df_train[,outcome.var])=="Categorical"){
      p<-ggplot(df_train,aes(get(outcome.var), as.factor(get(input$show_vars2))))
      p<-p+geom_boxplot(fill="#C1D4F7")
      p<-p+labs(title = paste("Boxplot of", input$show_vars2, "vs.", outcome.var), x=outcome.var, y=input$show_vars2)
      ggplotly(p)
    }else{
      dat <- data.frame(table(df_train[,input$show_vars2],df_train[,outcome.var]))
      names(dat) <- c(input$show_vars2, outcome.var,"Count")
      ggplot(data=dat, aes_string(x=as.factor(input$show_vars2), y=Count, fill=outcome.var)) + geom_bar(stat="identity", position = "dodge")
    }
  })

  
  data <- reactive({
    sort1 <- switch(input$sort1,
                   "abs" = "abs",
                   "corr" = "corr",
                   "abs")
  })

  output$corr.plot.outcome <- renderPlot({
    sort=input$sort1
    corr.plot.outcome(df_train, outcome=outcome.var, sort=sort)
  })
}