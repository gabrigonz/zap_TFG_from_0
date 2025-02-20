from init_db import crear_tablas 
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("CSRF_TOKEN")
csrf = CSRFProtect(app)

crear_tablas()

@app.route("/", methods=['GET'])
def home():
    return "✅ API de Auditoría de Seguridad Activa"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)