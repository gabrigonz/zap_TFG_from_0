from init_db import crear_tablas 
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from flask_cors import CORS
from routes import bp
from forms import ScanForm

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [f"http://192.168.1.{i}" for i in range(1, 255)]}})
app.config["SECRET_KEY"] = os.getenv("CSRF_TOKEN")
csrf = CSRFProtect(app)
app.register_blueprint(bp)
crear_tablas()
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/scan", methods=["GET", "POST"])
def scan():
    form = ScanForm()
    return render_template("scan.html", form=form)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)