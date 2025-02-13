from openai import OpenAI
from dotenv import load_dotenv
import os
from knowledge_rag import search_knowledge

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def save_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
    return

import re
def remove_triple_backticks(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    cleaned_content = re.sub(r'```(?:\w+)?\n?|```', '', content)
    with open(file_path, 'w') as file:
        file.write(cleaned_content)

def create_list_of_questions(content):
    cleaned_content = re.sub(r'```(?:\w+)?\n?|```', '', content)
    questions = cleaned_content.split("\n")
    return questions

def generate_code():
    print("Generating initial code")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    framework_functions = read_file("knowledge/code.txt")
    experimental_design = read_file("knowledge/paper.txt")
    completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-thinking-exp:free",
    messages=[
        {"role": "user", 
         "content": "You are a research software engineer that is tasked with writing a complete Python code snippet (using an existing simulation framework) that recreates a given human experiment from start to finish. Please stick to modifying the code provided in the repository versus writing random new code. You should also include the necessary imports and any necessary dependencies. Do not include any explanations or comments. Only provide the code snippet delimited by triple backticks. Please use load_dotenv() to load the OPENAI_API_KEY environment variable."},
        {"role": "user", 
         "content": f"Framework Functions: {framework_functions}. Experimental Design: {experimental_design}."},
    ],
    )   
    draft_code = completion.choices[0].message.content
    print("Thinking of ways to improve the code")
    completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-thinking-exp:free",
    messages=[
        {"role": "user", 
         "content": "You are a research software engineer that is tasked with writing a complete Python code snippet (using an existing simulation framework). Think of 10 ways to improve the current code snippet to better recreate the human experiment with in-depth accuracy. Modify these as questions to search the Github repo's documentation for answers. Please return this as a list surrounded by triple backticks, each question on a new line. No other formatting is necessary, ex. bullet points, dashes, or numbers."},
        {"role": "user", 
         "content": f"Framework Functions: {framework_functions}. Experimental Design: {experimental_design}. Current Code: {draft_code}."},
    ],
    )   
    output = completion.choices[0].message.content
    questions = [str(q) + " Return me the code." for q in create_list_of_questions(output)]
    qa_pairs = {}
    for question in questions:
        answer = search_knowledge(question)
        qa_pairs[question] = answer
    print("Generating final code")
    completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-thinking-exp:free",
    messages=[
        {"role": "user", 
         "content": "You are a research software engineer that is tasked with writing a complete Python code snippet (using an existing simulation framework) that recreates a given human experiment from start to finish. Please stick to modifying the code provided in the repository versus writing random new code. You should also include the necessary imports and any necessary dependencies. Do not include any explanations or comments. Only provide the code snippet delimited by triple backticks. Please use load_dotenv() to load the OPENAI_API_KEY environment variable. Please use the provided QA pairs to improve the current code."},
        {"role": "user", 
         "content": f"Framework Functions: {framework_functions}. Experimental Design: {experimental_design}. Current Code: {draft_code}. QA Pairs: {qa_pairs}."},
    ],
    )   
    final_code = completion.choices[0].message.content
    save_file("output/final_code.py", final_code)
    remove_triple_backticks("output/final_code.py")
    return

def fix_code(current_error):
    print("Fixing code")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    framework_functions = read_file("knowledge/code.txt")
    experimental_design = read_file("knowledge/paper.txt")
    current_code = read_file("output/final_code.py")
    #use search_knowledge to search for the answer to the error
    solution = search_knowledge("Why am I getting this error?" + current_error) 
    completion = client.chat.completions.create(
    model="openai/o3-mini-high",
    messages=[
        {"role": "user", 
         "content": "You are a research software engineer that is tasked with fixing a given Python code snippet (using an existing simulation framework) that recreates a given human experiment from start to finish. Please add evaluation metrics to the code snippet and print them, so I can compare the performance of the code to the human experiment. Please stick to modifying the code provided in the repository versus writing random new code. You should also include the necessary imports and any necessary dependencies. Do not include any explanations or comments. Only provide the code snippet delimited by triple backticks. Please use load_dotenv() to load the OPENAI_API_KEY environment variable."},
        {"role": "user", 
         "content": f"Framework Functions: {framework_functions}. Current Code {current_code}. Current Error: {current_error}. Potential Solution: {solution}"},
    ],
    )
    final_code = completion.choices[0].message.content
    save_file("output/final_code.py", final_code)
    remove_triple_backticks("output/final_code.py")
    return 

if __name__ == "__main__":
    generate_code()