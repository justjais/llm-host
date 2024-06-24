from flask import Flask 
from .pr_explanation import pr_explanation
 
app = Flask(__name__) 
 
@app.route('/')
def home(): 
    response = pr_explanation()
    return response
 
if __name__ == '__main__': 
    app.run(debug=True)