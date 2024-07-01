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
    for question in questions:
        answer = text2sql_instance.run_query(question)
        answers.append(answer)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        counter += 1
        time.sleep(30)
        # Print the number of questions left
        print(f"Questions left: {len(questions) - counter}")

    # Save the answers to a file (optional)
    with open("results_standard.txt", "w") as f:
        for question, answer in zip(questions, answers):
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n\n")

    print("Evaluation completed. Answers are stored in answers.txt.")
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
    for question in questions:
        answer = sql_agent.query_agent(question)
        answers.append(answer)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        counter += 1
        time.sleep(30)
        # Print the number of questions left
        print(f"Questions left: {len(questions) - counter}")

    # Save the answers to a file (optional)
    with open("results_agent.txt", "w") as f:
        for question, answer in zip(questions, answers):
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n\n")

    print("Evaluation completed. Answers are stored in answers.txt.")
else:
    pass
