from flask import Flask, request, jsonify,render_template
from flask_pymongo import PyMongo
from bson import ObjectId
import os

app = Flask(__name__)


app.config["MONGO_URI"] = "mongodb+srv://kayush0712:Ayush%40123@demo-cluster.s0jc1hf.mongodb.net/sample_mflix?retryWrites=true&w=majority&appName=demo-cluster"
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

    

@app.route("/insert_movie", methods=["POST"])
def insert_movie():

    title = request.form.get('title')
    year = request.form.get('year')

    if title and year:
        mongo.db.movies.insert_one({'title': title, 'year': int(year)})
        return f"Inserted movie: {title} ({year})"
    return "Missing title or year"


@app.route("/update_movie", methods=["POST"])
def update_movie():

    title = request.form.get('title')
    year = request.form.get('year')

    if title and year:
        mongo.db.movies.update_one(
            {"title": title},
            {"$set": {"year": int(year)}}
        )
        return f"Updated movie: {title} ({year})"
    return "Missing title or year"

@app.route("/delete_movie", methods=["POST"])
def delete_movie():

    title = request.form.get('title')

    if title:
        mongo.db.movies.delete_one({"title": title})
        return f"Deleted movie: {title}"
    return "Missing title"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))