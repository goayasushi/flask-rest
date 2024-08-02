from flask import Flask
from flask import request,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

app = Flask(__name__)

cors_origins = os.getenv('CORS_ORIGINS', '*')

cors = CORS(app, resources={r"/*": {"origins": cors_origins}})

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

@app.route("/articles")
def get_articles():
    articles = Post.query.order_by(Post.created_at.desc()).all()
    
    articles_list = [{"id": article.id, "title": article.title, "body": article.body, "created_at": article.created_at  } for article in articles]
    return jsonify(articles_list), 200

@app.route("/create", methods=["POST"])
def create():
      data = request.get_json() 
      
      post = Post(title=data["title"], body=data["body"])

      db.session.add(post)
      db.session.commit()
      return jsonify({"message": "Post created"}), 201 

@app.route("/<int:id>/update", methods=["GET"])
def get_article(id):
    article = Post.query.get_or_404(id)
    return jsonify({"id": article.id, "title": article.title, "body": article.body, "created_at": article.created_at}), 200

@app.route("/<int:id>/update", methods=["PUT"])
def update_article(id):
    data = request.get_json()
    article = Post.query.get_or_404(id)
    article.title = data.get("title", article.title)
    article.body = data.get("body", article.body)
    db.session.commit()
    return jsonify({"message": "Post updated"}), 200

@app.route("/<int:id>/delete", methods=["DELETE"])
def delete_article(id):
    try:
        article = Post.query.get_or_404(id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({"message": "Post deleted"}), 200
    except Exception as e:
        print(f"Error deleting article: {e}")
        return jsonify({"error": "Delete failed"}), 400

if __name__ == "__main__":
    app.run(debug=True)