from init_db import crear_tablas 
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [f"http://192.168.1.{i}" for i in range(1, 255)]}})
app.config["SECRET_KEY"] = os.getenv("CSRF_TOKEN")
csrf = CSRFProtect(app)

crear_tablas()

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)