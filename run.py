from github_utils import github_run
from paper_utils import paper_run, compare_results
from agent_utils import generate_code, fix_code
from execute_code import execute_code
import time

def run(repo_url, update_paper, update_github, generate_code, fix_attempts):
    if update_paper:
        paper_run()
    if update_github:
        github_run(repo_url)
    if generate_code:
        generate_code()
    errors_exist, error = execute_code()
    attempts = 1
    while errors_exist and attempts < fix_attempts+1:
        print(f"Attempt {attempts} to fix the code")
        fix_code(error)
        errors_exist, error = execute_code()
        attempts += 1
    if errors_exist:
        print("Max attempts reached. Unable to fix the code.")
    else:
        simulation_results = error
        compare_results(simulation_results)
    return

if __name__ == "__main__":
    repo_url = "https://github.com/microsoft/TinyTroupe"
    start = time.time()
    run(repo_url, update_paper=False, update_github=False, generate_code=False, fix_attempts=10)
    end = time.time()
    print(f"Total Time: {end - start} seconds")
