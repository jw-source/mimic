import os
import requests
import zipfile
import tempfile
import shutil
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
import os

def download_repo(url):
    url = url.rstrip('/')
    if not url.endswith('.git'):
        url = url.replace('.git', '')
    zip_url = f"{url}/archive/main.zip"
    temp_dir = tempfile.mkdtemp(dir=os.getcwd()) 
    response = requests.get(zip_url)
    zip_path = os.path.join(temp_dir, "main.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    os.remove(zip_path)
    return temp_dir

def all_files(directory_path):
    result = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py') or file.endswith('.pynb') or file.endswith('.md'):
                result.append(os.path.join(root, file))
    return result

def get_file_content(file_path):
    content = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def delete_repo(directory_path):
    shutil.rmtree(directory_path)

def documentation_exist(content):
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    completion = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "user", "content": "You are a research software engineer analyzing code from Github. Check if the provided content contains any documentation, such as function descriptions, parameter explanations, usage instructions, or API documentation. Only return 'True' if you find actual documentation explaining how to use the code. Return 'False' if there is no documentation or only basic code comments."},
            {
                "role": "user",
                "content": f"Content: {content}",
            }
        ],
    )
    res = completion.choices[0].message.content
    if "True" in res:
        return True
    else:
        return False

def dict_to_text(file_dict):
    text = ""
    for file_path, content in file_dict.items():
        text += f"\n=== File: {file_path} ===\n"
        text += content
        text += "\n\n"
    return text

def github_run(url):
    print("Running on GitHub")
    directory_path = download_repo(url)
    files = all_files(directory_path)
    documentation_files = {}
    for file in tqdm(files, desc="Processing files", unit="file"):
        file_content = get_file_content(file)
        d_exist = documentation_exist(file_content)
        if d_exist:
            documentation_files[file] = get_file_content(file)

    delete_repo(directory_path)

    documentation = dict_to_text(documentation_files)

    with open("knowledge/code.txt", "w", encoding='utf-8') as f:
        f.write("Documentation:\n" + documentation)
        f.close()
    
    return

if __name__ == "__main__":
    github_run("https://github.com/microsoft/TinyTroupe")