from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv
import requests
from io import BytesIO

def paper_run(url):
    print("Extracting experimental design")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    response = requests.get(url)
    pdf = pdfplumber.open(BytesIO(response.content))
    paper_content = ""
    for page in pdf.pages:
        paper_content += page.extract_text()
    prompt = """Extract the experimental design from the given research paper:
    1. Goal and purpose of the experiment
    2. Independent variables and their ranges/values used
    3. Dependent variables and how they were measured
    4. Control variables and their fixed values
    5. Experimental conditions and their specific parameters
    6. Number of trials/iterations/samples
    7. Any specific thresholds or cutoff values used
    8. Qualitative and quantitative results of the experiment, including their significance and interpretation
    DO NOT GENERATE ANY PSEUDOCODE
    """
    completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-thinking-exp:free",
    messages=[
        {"role": "user", 
         "content": prompt},
        {"role": "user", 
         "content": f": Paper: {paper_content}"},
    ],
    )   
    final = completion.choices[0].message.content
    with open("knowledge/paper.txt", "w", encoding='utf-8') as f:
        f.write(final)
    return final

if __name__ == "__main__":
    paper = paper_run("https://arxiv.org/pdf/2409.08357v1")
    print(paper)
