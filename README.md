# Mimic

#### 1. Project Setup
```python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### 2. Convert .env.txt file to .env (add OpenRouter and OpenAI API keys)
```
mv .env.txt .env
```

#### 3. Set up Modal (for virtual sandbox to execute code)
##### 4. Sign up for a free account at https://modal.com/signup
```
pip install modal
modal setup
```

#### 5. Download your research paper to simulate and move it to the knowledge folder (paper.pdf)

#### 6. Get the url of the framework you're interested in (e.g., TinyTroupe), and copy the url to the run.py file

#### 7. Run the run.py file
```
python run.py
```
