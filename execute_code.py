import os
from dotenv import load_dotenv
import modal

def execute_code():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    app = modal.App.lookup("mimic-modal", create_if_missing=True)
    image = (
        modal.Image.debian_slim(python_version="3.10") 
        .apt_install("git")
        .run_commands(
            "git clone https://github.com/microsoft/TinyTroupe /root/TinyTroupe",
            "cd /root/TinyTroupe && pip install .",
            "pip install python-dotenv",
            f"echo 'OPENAI_API_KEY={api_key}' |> /root/TinyTroupe/.env",
        )
        .add_local_file("output/final_code.py", "/root/TinyTroupe/examples/final_code.py")
    )

    print("Creating sandbox with TinyTroupe environment")
    with modal.enable_output():
        sb = modal.Sandbox.create(
            image=image,
            workdir="/root/TinyTroupe",
            app=app,
        )
    try:
        print("Running final_code.py")
        process = sb.exec("python", "examples/final_code.py")
        output = process.stdout.read()
        print(output)
        error = process.stderr.read()
        print(error)
    finally:
        sb.terminate()
    if error:
        return True, error
    else:
        return False, output

if __name__ == "__main__":
    execute_code()