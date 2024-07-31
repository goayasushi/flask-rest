from flask import Flask
from flask import request,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone("Asia/Tokyo")))

with app.app_context():
    db.create_all()

@app.route("/hello")
def home():
    return "Hello, Flask!"

@app.route("/create", methods=["POST"])
def create():
      data = request.get_json() 
      
      post = Post(title=data["title"], body=data["body"])

      db.session.add(post)
      db.session.commit()
      return jsonify({"message": "Post created"}), 201 

if __name__ == "__main__":
    app.run(debug=True)