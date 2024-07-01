from text2sql_loader import text2SQL
from pathlib import Path
import os
import time
import pandas as pd

cur_dir = Path(os.getcwd())
print(cur_dir)
target_dir = cur_dir.parent / 'welcomeback_dev/data_science_folder/cleaned'
print(target_dir)

# Paths to the new CSV files
csv_file_paths = [os.path.join(target_dir, 'hourly_orders_detailed_vanilla.csv'),
                  os.path.join(target_dir, 'rfm_data.csv')]

# List of 10 questions to evaluate
questions = [
    "Retrieve the total gross revenue for each day of the week",

    "What are my number of unique customers placing orders each month?",

    "What are my average order value for each type of order channel?",

    "List the top 5 zip codes by total number of orders",

    "List my average order value per month",

    "What is the average gross revenue by customer segments?",

    "What is the correaltion between frequency and monetary scores?",

    "What are the total number of orders placed during weekends versus weekdays?",

    "What is the percentage of total revenue made by B2B orders?",

    "Give me a summary of the last complete month's data across all order channels."
]

questions_2 = [
    "Total Revenue for the Year",
    "Number of Orders per Customer Segment",
    "Monthly Change in Average Order Value (AOV)",
    "Top 10 Highest Grossing Customers and Their Last Order Date",
    # "Year-over-Year Growth Rate by Order Type",
    "What is my customer Lifetime Value (CLV) by customer segment?",

]

# Process the new CSV files
text2sql_instance = text2SQL()
text2sql_instance.load_data(csv_file_paths)
text2sql_instance.process_tables()
text2sql_instance.create_sql_database()
text2sql_instance.setup_query_pipeline()

# Store answers in a list
answers = []
counter = 0
# Submit the questions and store the answers
for question in questions_2:
    answer = text2sql_instance.run_query(question)
    answers.append(answer)
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    counter += 1
    time.sleep(30)
    # Print the number of questions left
    print(f"Questions left: {len(questions_2) - counter}")

# Save the answers to a file (optional)
with open("results_2.txt", "w") as f:
    for question, answer in zip(questions_2, answers):
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n\n")

print("Evaluation completed. Answers are stored in answers.txt.")
