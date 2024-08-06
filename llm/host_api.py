"""flask app to host implementation as API"""
from flask import Flask
from .pr_explanation_poc import pr_explanation

app = Flask(__name__)

@app.route('/')
def home():
    """API endpoint hosting over localhost"""
    response = pr_explanation()
    return response

if __name__ == '__main__':
    app.run(debug=True)
