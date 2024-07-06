from text2sql_loader import text2SQL
from SQLAgent_V2 import SQLAgent_V2
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
level_0_questions = [
    "What is the total number of entries in the orders dataset?",
    "List all unique years in the dataset.",
    "What is the highest gross revenue recorded for any order?",
    "Is there any order data for the month of January?",
    "Are there any entries on the most recent day of data collection?",
    "Name one product category available in the dataset.",
    "Does the dataset contain orders from the postcode '12345'?",
    "Name one customer by their ID.",
    "Is there any order data from the B2B channel?",
    "Does the dataset include any internal orders?"
]


level_1_questions = [
    "How many total orders are recorded?",
    "What is the total gross revenue?",
    "How many unique products have been sold?",
    "Count the number of orders from the most recent date.",
    "Find the minimum and maximum gross revenue per order.",
    "How many orders were placed in the last week of 2023?",
    "What is the total number of B2B orders?",
    "What is the total number of marketplace orders?",
    "What is the average order value (AOV)?",
    "What is the earliest date in the dataset?"
]

level_2_questions = [
    "What is the most recent date in the dataset?",
    "How many unique customers are there?",
    "What is the average number of orders per customer?",
    "What are the top 5 most common postcodes for orders?",
    "List the top 5 most frequent product names by order count.",
    "What is the average total gross revenue from internal orders?",
    "How many B2B orders are there?",
    "Which day of the week has the highest average orders?",
    "What is the total cost of goods sold (COGS)?",
    "What is the total revenue for B2B orders?"
]

level_3_questions = [
    "How many products are in the 'Sports' main category?",
    "What is the average revenue per month?",
    "Which customer segment has the highest average order value?",
    "How many orders are above the average order value?",
    "What is the most common RFM segment?",
    "What percentage of total orders are from internal website?",
    "Which product category has the highest total revenue?",
    "Retrieve the total number of orders for each month.",
    "What is the total number of unique products sold each month?"
    "What is my best selling product?",
]

level_4_questions = [
    "Calculate total orders, total revenue, and average order value for each month.",
    "Compare the total number of orders and total revenue per month to the previous month.",
    "Examine the monthly trend of average COGS.",
    "Identify the postcode with the greatest increase in orders year-over-year.",
    "What is the average monthly revenue growth over the year?",
    "Identify the customer with the highest total revenue.",
    "Calculate the average monetary value per RFM segment and compare it with the average order value (AOV) of the entire dataset.",
    "Evaluate the effectiveness of the marketplace channel based on total orders and revenue.",
    "Analyze seasonal patterns in order volumes by month and day of the week.",
    "Compare revenue from B2B orders to revenue from Marketplace orders."
]

usr_input = input("RAG Test: standard_rag or agent_rag?")

if usr_input == "standard_rag":

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
    for question in level_0_questions:
        answer = text2sql_instance.run_query(question)
        answers.append(answer)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        counter += 1
        time.sleep(30)
        # Print the number of questions left
        print(f"Questions left: {len(level_0_questions) - counter}")

    # Save the answers to a file
    with open("results_standard.txt", "w") as f:
        for question, answer in zip(level_0_questions, answers):
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n\n")

    print("Evaluation completed. Answers are stored in answers_level4.txt.")
else:
    pass

if usr_input == "agent_rag":

    # Process the new CSV files
    context_prompt = "The data is from an e-commerce company in Switzerland from January 2023 to December 2023."
    sql_agent = SQLAgent_V2(
        csv_file_paths, ["hourly_orders_detailed_vanilla", "rfm_data"], context_prompt=context_prompt)
    sql_agent.create_db(
        csv_file_paths, ["hourly_orders_detailed_vanilla", "rfm_data"])
    sql_agent.instantiate_agent()

    # Store answers in a list
    answers = []
    counter = 0
    # Submit the questions and store the answers
    for question in level_1_questions:
        answer = sql_agent.query_agent(question)
        answers.append(answer)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        counter += 1
        time.sleep(30)
        # Print the number of questions left
        print(f"Questions left: {len(level_1_questions) - counter}")

    # Save the answers to a file
    with open("results_agent.txt", "w") as f:
        for question, answer in zip(level_1_questions, answers):
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n\n")

    print("Evaluation completed. Answers are stored in answers.txt.")
else:
    pass
