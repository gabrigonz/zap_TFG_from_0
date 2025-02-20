from init_db import crear_tablas 
from flask import Flask

app = Flask(__name__)

crear_tablas()

@app.route("/")
def home():
    return "✅ API de Auditoría de Seguridad Activa"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)