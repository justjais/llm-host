# llm-host
LLM hosted over: `"http://127.0.0.1:5000"`. Currently, the POC code uses static `git diff`.

### Install python requirements
    python -m venv venv
    source venv/bin/activate
    # If necessary: pip install pip-tools
    pip-compile requirements.in
    pip install -r requirements.txt 

### Steps to run POC python script
1. Install the python requirements
2. Run the python LLM host as: `python -m llm.host_api`
3. Run the bot-scanner as: `go run cmd/github-scanner/main.go`

# Steps to LLM based PR explanation
1. Install the python requirements
2. Run the python script as: `python llm_pr_explanation.py`

### Pre-requisites:
1. Script run tested using Python 3.12.1 & 3.11.9
2. Ollama installed with different models, and `nomic-embed-text` for embeddings
