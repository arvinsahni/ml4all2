library(markdown)

navbarPage("EDA",
           tabPanel("Inspect data",
                    fluidPage(
                      fluidRow(
                        column(2,
                          conditionalPanel(
                            'input.dataset === "Training"',
                            checkboxGroupInput('show_vars_dtrain', 'Columns in dataset to show:',
                                              names(df_train), selected = names(df_train))
                          ),
                          conditionalPanel(
                            'input.dataset === "Testing"',
                            checkboxGroupInput('show_vars_dtest', 'Columns in dataset to show:',
                                               names(df_test), selected = names(df_test))
                          )
                        ),
                        
                        column(10,
                          tabsetPanel(
                            id = 'dataset',
                            tabPanel('Training', DT::dataTableOutput('dtrain')),
                            tabPanel('Testing', DT::dataTableOutput('dtest'))
                          )
                        )
                      )
                    )
           ),
           
           tabPanel("Data summary",
                    fluidPage(
                      fluidRow(
                        column(2,
                          radioButtons('show_vars', 'Variable in dataset to plot:',
                                             names(df_train)[-1], selected = names(df_train)[-1][1]),
                          br()
                        ),
                        
                        column(10,
                          fluidRow(
                            column(5,
                              h4("Training data:"),
                              plotlyOutput("summary.plot.train"),
                              tableOutput("summary.table.train")
                            ),
                            
                            column(5,
                              h4("Testing data:"),
                              plotlyOutput("summary.plot.test"),
                              tableOutput("summary.table.test")
                            )
                          )
                        )
                      )
                    )
           ),
           
           tabPanel("Missing data",
                    splitLayout(
                        plotOutput("miss.plot"),
                        tableOutput("miss.table")
                    )
           ),
           
           tabPanel("Versus response variable",
                    fluidPage(
                      fluidRow(
                        column(2,
                          radioButtons('show_vars2', 'Variable in dataset to plot against outcome var:',
                                       target.vars, selected = target.vars[1]),
                          br()
                        ),
                        
                        column(10,
                          plotlyOutput("relation.plot")
                        )
                      )  
                    )
           ),
           
           
           tabPanel("Correlations vs. outcome",
                    sidebarLayout(
                      
                      sidebarPanel(
                        radioButtons("sort1", "Sort by:",
                                     c("Absolute value" = "abs",
                                       "Nominal value" = "corr")),
                        br()
                      ),
                      
                      mainPanel(
                        plotOutput("corr.plot.outcome")
                      )
                    )
           )
           
)