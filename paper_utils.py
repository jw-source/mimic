from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv
from agent_utils import read_file

def paper_run():
    print("Extracting experimental design")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    pdf = pdfplumber.open("knowledge/paper.pdf")
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

def compare_results(simulation_results):
    print("Comparing simulation results")
    load_dotenv()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
    experimental_results = read_file("knowledge/paper.txt")
    prompt = f"""Compare the results of the computer simulation to the results of the actual experiment described in the research paper. Provide a detailed comparison of the two sets of results, including any similarities and differences."""
    completion = client.chat.completions.create(
    model="openai/o3-mini",
    messages=[
        {"role": "user", 
         "content": prompt},
        {"role": "user", 
         "content": "Simulation Results: " + simulation_results + ". Actual Results: " + experimental_results},
    ],
    )   
    comparison = completion.choices[0].message.content
    print(comparison)
    return