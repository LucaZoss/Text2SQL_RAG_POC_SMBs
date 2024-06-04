-- hourly_orders_vanilla
RangeIndex: 12968 entries, 0 to 12967
Data columns (total 19 columns):
 #   Column                         Non-Null Count  Dtype                       Description
---  ------                         --------------  -----                --------------------------          
 0   date                           12968 non-null  datetime64[ns, UTC]     Hourly Data from Jan-Dec 23     
 1   order_id                       12968 non-null  int64                   Unique Order Identifier              
 2   postcode                       12961 non-null  object                  Zip Code Switzerland            
 3   day_of_week                    12968 non-null  object                  Day of Week             
 4   tot_orders                     12968 non-null  int64                   Tot_Orders             
 5   tot_gross_revenue              12968 non-null  float64                 Gross_Revenue                        
 6   tot_cogs                       12901 non-null  float64                 Cost of Goods Sold            
 7   tot_orders_marketplace         12968 non-null  int64                   Marketplace Orders             
 8   tot_orders_int                 12968 non-null  int64                   Direct Website Orders              
 9   tot_orders_b2b                 12968 non-null  int64                   B2B Orders              
 10  tot_gross_revenue_mrktpl       12968 non-null  float64                 Gross Revenue Marketplaces                          
 11  tot_gross_revenue_int          12968 non-null  float64                 Gross Revenue Direct           
 12  tot_gross_revenue_b2b          12968 non-null  float64                 Gross Revenue B2B           
 13  AOV                            12968 non-null  float64                 Average Order Value (depreciated?)            
 14  lag_weekday_tot_orders         12961 non-null  float64                 Previous amount of orders normalized on week day (depreciated)           
 15  lag_weekday_tot_gross_revenue  12961 non-null  float64                 Previous amount of gross revenue normalized on week day (depreciated)
 16  lag_weekday_AOV                12961 non-null  float64                 Previous amount of AOV normalized on week day (depreciated)
 17  customer_id                    12968 non-null  int64                   Unique customer identifier
 18  datetime_rounded               12968 non-null  datetime64[ns, UTC]     datetime_rounded (depreciated)

-- hourly_orders_weather_flavoured

RangeIndex: 12968 entries, 0 to 12967
Data columns (total 26 columns):
 #   Column                         Non-Null Count  Dtype       Description             
---  ------                         --------------  -----       -------------------------                         
 18  temperature_2m                 12968 non-null  float64     Temperature at 2m            
 19  relative_humidity_2m           12968 non-null  float64     Humidity Level            
 20  precipitation                  12968 non-null  float64     Precepition           
 21  rain                           12968 non-null  float64     Rain            
 22  snowfall                       12968 non-null  float64     Snowfall            
 23  weather_code                   12968 non-null  float64     WMO Weather Code : array([51.,  0.,  3.,  2., 71., 53.,  1., 73., 55., 61., 63., 75., 65.])           
 24  cloud_cover                    12968 non-null  float64     Cloud cover percentage 0= not covered           
 25  sunshine_duration              12968 non-null  float64     Sunshine Duration in min or seconds (to check)

 --> Check this website for more info: [url]https://open-meteo.com/en/docs/historical-weather-api#latitude=47.0002&longitude=8.0143&hourly=temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,weather_code,cloud_cover,sunshine_duration&daily=&timezone=auto

 -- hourly_orders_detailed_vanilla + _en_
 RangeIndex: 25019 entries, 0 to 25018
Data columns (total 22 columns):
 #   Column                         Non-Null Count  Dtype  
---  ------                         --------------  -----  
 18  product_name                   25009 non-null  object 
 19  product_id                     25009 non-null  float64
 20  main_category                  25009 non-null  object      Product Main Categories
 21  sub_category                   25009 non-null  object      Product Sub Categories