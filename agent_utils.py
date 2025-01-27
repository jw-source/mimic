from openai import OpenAI
from dotenv import load_dotenv
import os

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

def generate_code():
    print("Generating code")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    framework_functions = read_file("knowledge/code.txt")
    experimental_design = read_file("knowledge/paper.txt")
    completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-thinking-exp:free",
    messages=[
        {"role": "user", 
         "content": "You are a research software engineer that is tasked with writing a complete Python code snippet (using an existing simulation framework) that recreates a given human experiment from start to finish. Please add evaluation metrics to the code snippet so I can compare the performance of the code to the human experiment. The code should be able to run on a local machine. Please stick to modifying the code provided in the repository versus writing random new code. You should also include the necessary imports and any necessary dependencies. Do not include any explanations or comments. Only provide the code snippet delimited by triple backticks."},
        {"role": "user", 
         "content": f"Framework Functions: {framework_functions}. Experimental Design: {experimental_design}."},
    ],
    )   
    final_code = completion.choices[0].message.content
    save_file("output/final_code.py", final_code)
    remove_triple_backticks("output/final_code.py")
    return final_code

if __name__ == "__main__":
    code = generate_code()
    print(code)