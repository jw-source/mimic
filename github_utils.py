import os
import requests
import zipfile
import tempfile
import shutil
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm
import google.generativeai as genai
from dotenv import load_dotenv
import os

def download_repo(url):
    url = url.rstrip('/')
    if not url.endswith('.git'):
        url = url.replace('.git', '')
    zip_url = f"{url}/archive/main.zip"
    temp_dir = tempfile.mkdtemp(dir=os.getcwd()) 
    print(f"Temporary directory created at: {temp_dir}")
    response = requests.get(zip_url)
    zip_path = os.path.join(temp_dir, "main.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    os.remove(zip_path)
    print(f"Files extracted to: {temp_dir}")
    return temp_dir

def get_tree(directory_path):
    result = []
    for root, dirs, files in os.walk(directory_path):
        level = root.replace(directory_path, '').count(os.sep)
        indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
        result.append(f'{indent}{os.path.basename(root)}/')
        for file in files:
            indent = '│   ' * level + '├── '
            result.append(f'{indent}{file}')
    return '\n'.join(result)

def all_files(directory_path):
    result = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                result.append(os.path.join(root, file))
    return result

def get_file_content(file_path):
    content = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def delete_repo(directory_path):
    shutil.rmtree(directory_path)
    print(f"Successfully deleted: {directory_path}")

class Parameter(BaseModel):
    var_exists: bool

def parameters_exist(content):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "developer", "content": "You are a code reviewer that checks if a given code snippet contains any parameters that are designed for end-user control. If so, only return the word 'True'. This does not include internal variables, developer-only settings, or any parameters that are not intended for end-user manipulation. Else return 'False'."},
            {
                "role": "user",
                "content": f"Content: {content}",
            }
        ],
        response_format=Parameter
    )
    return completion.choices[0].message.parsed.var_exists

def concat_output(tree_content, relavant_files):
    output = ""
    output+= tree_content
    line_seperator = '\n' + '-'*100 + '\n'
    output += line_seperator
    for file in relavant_files.keys():
        output += f"File: {file}\n"
        output += f"Content: {relavant_files[file]}\n"
        output += line_seperator
    return output

def aggregate_functions(code):
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    print("Drafting initial list of functions...")
    prompt = """Extract a detailed list of end-user functions from the following repository code: Please provide documentation for each function, including the name, purpose, parameters, return value."""
    response = model.generate_content([prompt, code])
    draft = response.text
    print("Giving constructive criticism...")
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    prompt = """Please give constructive criticism for this list of end-user functions below. For example, if a function is not needed, please explain why. If a function is missing, please explain why and provide documentation, including the name, purpose, parameters, return value."""
    response = model.generate_content([prompt, draft])
    edits = response.text
    print("Finalizing list of functions...")
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    prompt = """Using the list of end-user functions and constructive criticism, please provide a final list of end-user functions that can be used to recreate the experiment from start to finish. Please provide documentation for each function, including the name, purpose, parameters, return value."""
    response = model.generate_content([prompt, draft, edits])
    final= response.text
    return final

def extract_examples(code):
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Extracting examples")
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    prompt = """Please extract a list of example use-cases from the following repository. These should be a list of code snippets seperated by a new line. DO NOT MODIFY THE EXAMPLES."""
    response = model.generate_content([prompt, code])
    examples = response.text
    return examples

def github_run(url):
    directory_path = download_repo(url)
    tree_content = get_tree(directory_path)
    files = all_files(directory_path)
    relavant_files = {}
    for file in tqdm(files, desc="Processing files", unit="file"):
        file_content = get_file_content(file)
        output = parameters_exist(file_content)
        if output:
            relavant_files[file] = get_file_content(file)
    delete_repo(directory_path)
    output = concat_output(tree_content, relavant_files)
    functions = aggregate_functions(output)
    examples = extract_examples(output)
    with open("knowledge/code.txt", "w", encoding='utf-8') as f:
        f.write("Functions:\n" + functions + "\n\nExamples:\n" + examples)
    return output

if __name__ == "__main__":
    relevant_code = github_run("https://github.com/microsoft/TinyTroupe")
    print(relevant_code)