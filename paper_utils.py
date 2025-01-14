import google.generativeai as genai
import httpx
import base64
import os
from dotenv import load_dotenv

def paper_run(url):
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    doc_data = base64.standard_b64encode(httpx.get(url).content).decode("utf-8")
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
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
    print("Extracting the experimental design from the paper...")
    response = model.generate_content([{'mime_type':'application/pdf', 'data': doc_data}, prompt])
    draft = response.text
    print("Giving constructive criticism...")
    prompt = """Please give constructive criticism for this experimental design. Please add more details such that I can better understand this experiment without reading the paper and be able to fully replicate the results. DO NOT GENERATE ANY PSEUDOCODE"""
    response = model.generate_content([{'mime_type':'application/pdf', 'data': doc_data}, draft, prompt])
    edits = response.text
    print("Creating a final experimental design...")
    prompt = """Using the initial experimental design and constructive criticism, please create a final, detailed documentation for the experiment's experimental design. DO NOT GENERATE ANY PSEUDOCODE"""
    response = model.generate_content([draft, edits, prompt])
    final=response.text
    with open("knowledge/paper.txt", "w", encoding='utf-8') as f:
        f.write(final)
    return final

if __name__ == "__main__":
    paper = paper_run("https://arxiv.org/pdf/2409.08357v1")
    print(paper)
