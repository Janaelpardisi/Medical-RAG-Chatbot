from flask import Flask, render_template, request
from main import ask_disease_bot  
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])

def index():
    response = ""
    if request.method == "POST":
        user_input = request.form["user_input"]
        response = ask_disease_bot(user_input)
    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True , port = 5500)