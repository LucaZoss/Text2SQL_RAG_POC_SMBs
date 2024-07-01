Based on the descriptions of the tables `hourly_orders_vanilla` and `RFM`, here are 10 questions that you could ask your database:

1. **What is the total gross revenue for each day of the week?**
   ```sql
   SELECT day_of_week, SUM(tot_gross_revenue) as total_revenue
   FROM hourly_orders_vanilla
   GROUP BY day_of_week;
   ```

2. **How many unique customers placed orders each month?**
   ```sql
   SELECT EXTRACT(MONTH FROM date) as month, COUNT(DISTINCT customer_id) as unique_customers
   FROM hourly_orders_vanilla
   GROUP BY month;
   ```

3. **What is the average order value for each type of order channel (marketplace, direct website, B2B)?**
   ```sql
   SELECT AVG(tot_gross_revenue_mrktpl) as avg_mrktpl, AVG(tot_gross_revenue_int) as avg_int, AVG(tot_gross_revenue_b2b) as avg_b2b
   FROM hourly_orders_vanilla;
   ```

4. **Can you identify the top 5 zip codes by total number of orders?**
   ```sql
   SELECT postcode, SUM(tot_orders) as total_orders
   FROM hourly_orders_vanilla
   GROUP BY postcode
   ORDER BY total_orders DESC
   LIMIT 5;
   ```

5. **Monthly Trends in Average Order Value (AOV)**
   ```sql
   SELECT EXTRACT(MONTH FROM date) AS month, AVG(AOV) AS avg_aov
   FROM hourly_orders_vanilla
   GROUP BY month
   ORDER BY month;
   ```

6. **How does the average gross revenue vary between different customer segments?**
   ```sql
   SELECT RFM_Segment, AVG(monetary) as avg_monetary
   FROM RFM
   GROUP BY RFM_Segment;
   ```

7. **What is the correlation between frequency and monetary scores among customers?**
   ```sql
   SELECT CORR(frequency_score, monetary_score) as correlation
   FROM RFM;
   ```

8. **How many orders have been placed during weekends compared to weekdays?**
   ```sql
   SELECT CASE WHEN day_of_week IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END as type, COUNT(*) as order_count
   FROM hourly_orders_vanilla
   GROUP BY type;
   ```

9. **What percentage of total revenue comes from B2B orders?**
   ```sql
   SELECT (SUM(tot_gross_revenue_b2b) / SUM(tot_gross_revenue)) * 100 as percentage_b2b
   FROM hourly_orders_vanilla;
   ```

10. **Summary of the Latest Complete Month’s Data Across All Order Channels**
    ```sql
    SELECT 
    SUM(tot_orders_marketplace) AS total_marketplace_orders,
    SUM(tot_orders_int) AS total_direct_orders,
    SUM(tot_orders_b2b) AS total_b2b_orders,
    SUM(tot_gross_revenue_mrktpl) AS total_marketplace_revenue,
    SUM(tot_gross_revenue_int) AS total_direct_revenue,
    SUM(tot_gross_revenue_b2b) AS total_b2b_revenue
FROM hourly_orders_vanilla
WHERE EXTRACT(YEAR FROM date) = 2023
  AND EXTRACT(MONTH FROM date) = (SELECT MAX(EXTRACT(MONTH FROM date)) FROM hourly_orders_vanilla WHERE EXTRACT(YEAR FROM date) = 2023);


    ```


##### Python

1. **Total gross revenue for each day of the week:**
   ```python
   hourly_orders_vanilla.groupby('day_of_week')['tot_gross_revenue'].sum()
   ```

2. **Number of unique customers placing orders each month:**
   ```python
   hourly_orders_vanilla['month'] = hourly_orders_vanilla['date'].dt.month
   hourly_orders_vanilla.groupby('month')['customer_id'].nunique()
   ```

3. **Average order value for each type of order channel:**
   ```python
   hourly_orders_vanilla[['tot_gross_revenue_mrktpl', 'tot_gross_revenue_int', 'tot_gross_revenue_b2b']].mean()
   ```

4. **Top 5 zip codes by total number of orders:**
   ```python
   hourly_orders_vanilla.groupby('postcode')['tot_orders'].sum().nlargest(5)
   ```

5. **Monthly Trends in Average Order Value (AOV)**
   ```python
   hourly_orders_vanilla['month'] = hourly_orders_vanilla['date'].dt.month
   monthly_aov_trends = hourly_orders_vanilla.groupby('month')['AOV'].mean()
   ```

6. **Average gross revenue by customer segment:**
   ```python
   RFM.groupby('RFM_Segment')['monetary'].mean()
   ```

7. **Correlation between frequency and monetary scores:**
   ```python
   RFM[['frequency_score', 'monetary_score']].corr().iloc[0, 1]
   ```

8. **Orders placed during weekends versus weekdays:**
   ```python
   hourly_orders_vanilla['type'] = hourly_orders_vanilla['day_of_week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
   hourly_orders_vanilla.groupby('type').size()
   ```

9. **Percentage of total revenue from B2B orders:**
   ```python
   total_b2b_revenue = hourly_orders_vanilla['tot_gross_revenue_b2b'].sum()
   total_revenue = hourly_orders_vanilla['tot_gross_revenue'].sum()
   percentage_b2b = (total_b2b_revenue / total_revenue) * 100
   ```

10. **Summary of the Latest Complete Month’s Data Across All Order Channels**
    ```python
   hourly_orders_2023 = hourly_orders_vanilla[hourly_orders_vanilla['year'] == 2023]
   last_complete_month = hourly_orders_2023['month'].max()

   latest_month_data = hourly_orders_2023[hourly_orders_2023['month'] == last_complete_month]

   summary_last_month = latest_month_data.agg({
      'tot_orders_marketplace': 'sum',
      'tot_orders_int': 'sum',
      'tot_orders_b2b': 'sum',
      'tot_gross_revenue_mrktpl': 'sum',
      'tot_gross_revenue_int': 'sum',
      'tot_gross_revenue_b2b': 'sum'
   })

   summary_last_month

    ```

List of Questions:

- Retrieve the total gross revenue for each day of the week

- What are my number of unique customers placing orders each month?

- What are my average order value for each type of order channel?

- List the top 5 zip codes by total number of orders

- List my average order value per month

- What is the average gross revenue by customer segments?

- What is the correaltion between frequency and monetary scores?

- What are the total number of orders placed during weekends versus weekdays?

- What is the percentage of total revenue made by B2B orders?

- Give me a summary of the last complete month's data across all order channels.

# 2nd Trials
---
### Easy Questions
1. **Total Revenue for the Year**
   **SQL Query:**
   ```sql
   SELECT SUM(tot_gross_revenue) AS total_annual_revenue
   FROM hourly_orders_vanilla;
   ```
   **Python Code:**
   ```python
   total_revenue = hourly_orders_vanilla['tot_gross_revenue'].sum()
   ```

2. **Number of Orders per Customer Segment**
   **SQL Query:**
   ```sql
   SELECT RFM_Segment, COUNT(*) AS order_count
   FROM RFM
   GROUP BY RFM_Segment;
   ```
   **Python Code:**
   ```python
   orders_per_segment = RFM['RFM_Segment'].value_counts()
   ```

### Moderate Questions
3. **Monthly Change in Average Order Value (AOV)**
   **SQL Query:**
   ```sql
   SELECT EXTRACT(MONTH FROM date) AS month, AVG(AOV) AS monthly_aov
   FROM hourly_orders_vanilla
   GROUP BY month
   ORDER BY month;
   ```
   **Python Code:**
   ```python
   monthly_aov = hourly_orders_vanilla.groupby(hourly_orders_vanilla['date'].dt.month)['AOV'].mean()
   ```

4. **Top 10 Highest Grossing Customers and Their Last Order Date**
   **SQL Query:**
   ```sql
   SELECT customer_id, SUM(tot_gross_revenue) AS total_revenue, MAX(date) AS last_order_date
   FROM hourly_orders_vanilla
   GROUP BY customer_id
   ORDER BY total_revenue DESC
   LIMIT 10;
   ```
   **Python Code:**
   ```python
   top_customers = hourly_orders_vanilla.groupby('customer_id').agg({
       'tot_gross_revenue': 'sum',
       'date': 'max'
   }).nlargest(10, 'tot_gross_revenue')
   ```

### Hard Questions
5. **Year-over-Year Growth Rate by Order Type**
   **SQL Query:**
   ```sql
   SELECT EXTRACT(YEAR FROM date) AS year, 
          SUM(tot_orders_marketplace) AS marketplace_orders, 
          SUM(tot_orders_int) AS direct_orders,
          LAG(SUM(tot_orders_marketplace), 1) OVER (ORDER BY EXTRACT(YEAR FROM date)) AS last_year_marketplace,
          LAG(SUM(tot_orders_int), 1) OVER (ORDER BY EXTRACT(YEAR FROM date)) AS last_year_direct
   FROM hourly_orders_vanilla
   GROUP BY year;
   ```
   **Python Code:**
   ```python
   yearly_data = hourly_orders_vanilla.groupby(hourly_orders_vanilla['date'].dt.year).agg({
       'tot_orders_marketplace': 'sum',
       'tot_orders_int': 'sum'
   })
   yearly_data['marketplace_growth'] = yearly_data['tot_orders_marketplace'].pct_change() * 100
   yearly_data['direct_growth'] = yearly_data['tot_orders_int'].pct_change() * 100
   ```

6. **What is my customer life time value by customer segments**
   **SQL Query:**
   ```sql
   SELECT RFM.RFM_Segment, AVG(total_revenue) AS average_CLV
FROM (
    SELECT customer_id, SUM(tot_gross_revenue) AS total_revenue
    FROM hourly_orders_vanilla
    GROUP BY customer_id
) AS Revenue
JOIN RFM ON Revenue.customer_id = RFM.customer_id
GROUP BY RFM.RFM_Segment;
``` 
```python
   # Calculate total revenue per customer
   revenue_per_customer = hourly_orders_vanilla.groupby('customer_id')['tot_gross_revenue'].sum().reset_index()

   # Merge with RFM DataFrame
   revenue_per_customer = revenue_per_customer.merge(RFM[['customer_id', 'RFM_Segment']], on='customer_id')

   # Calculate average CLV per RFM Segment
   average_clv_per_segment = revenue_per_customer.groupby('RFM_Segment')['tot_gross_revenue'].mean()

   average_clv_per_segment
```
   