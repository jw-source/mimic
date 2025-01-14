from github_utils import github_run
from paper_utils import paper_run
from agent_utils import generate_code

def run(repo_url, paper_url, update_knowledge):
    if update_knowledge is True:
        github_run(repo_url)
        paper_run(paper_url)
    code = generate_code()
    return code

if __name__ == "__main__":
    repo_url = "https://github.com/microsoft/TinyTroupe"
    paper_url = "https://arxiv.org/pdf/2409.08357v1"
    run(repo_url, paper_url, update_knowledge=True)
