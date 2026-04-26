from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
from markupsafe import escape
from embeddings import embed_text
from llm import generate_movie_description
import os

app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb+srv://kayush0712:Ayush%40123@demo-cluster.s0jc1hf.mongodb.net/sample_mflix?retryWrites=true&w=majority&appName=demo-cluster")
mongo = PyMongo(app)


def _is_ajax_request():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _json_message(ok, message, status=200):
    return jsonify({"ok": ok, "message": message}), status

@app.route("/")
def index():
    movies = list(mongo.db.movies.find({}, {"_id": 0, "title": 1}))
    return render_template("index.html", movies=movies)


@app.route("/profile")
def profile():
    return render_template("profile.html")


    

@app.route("/insert_movie", methods=["POST"])
def insert_movie():
    title = request.form.get("title")
    year = request.form.get("year")

    if title and year:
        
        description = generate_movie_description(title, int(year))

        
        vector = embed_text(description)

        mongo.db.movies.insert_one({
            "title": title,
            "year": int(year),
            "description": description,
            "embedding": vector
        })

        msg = f"Movie added: {title} ({year})."
        if _is_ajax_request():
            return _json_message(True, msg)
        return msg

    msg = "Missing title or year."
    if _is_ajax_request():
        return _json_message(False, msg, 400)
    return msg


@app.route("/update_movie", methods=["POST"])
def update_movie():
    title = request.form.get("title")
    year = request.form.get("year")

    if title and year:
        mongo.db.movies.update_one({"title": title}, {"$set": {"year": int(year)}})
        msg = f"Movie updated: {title} (year {year})."
        if _is_ajax_request():
            return _json_message(True, msg)
        return msg
    msg = "Missing title or year."
    if _is_ajax_request():
        return _json_message(False, msg, 400)
    return msg


@app.route("/delete_movie", methods=["POST"])
def delete_movie():
    title = request.form.get("title")

    if title:
        mongo.db.movies.delete_one({"title": title})
        msg = f"Movie deleted: {title}."
        if _is_ajax_request():
            return _json_message(True, msg)
        return msg
    msg = "Missing title."
    if _is_ajax_request():
        return _json_message(False, msg, 400)
    return msg

@app.route("/renting", methods=["GET", "POST"])
def rent_movie_form():
    movie_title = request.form.get("title") if request.method == "POST" else request.args.get("title")

    if not movie_title:
        msg = "No movie title provided."
        if _is_ajax_request():
            return _json_message(False, msg, 400)
        return msg

    movie = mongo.db.movies.find_one({"title": movie_title})

    if not movie:
        msg = "Movie not found."
        if _is_ajax_request():
            return _json_message(False, msg, 404)
        return msg

    if request.method == "POST":
        phoneno = request.form.get("phoneno")

        if movie.get("copies", 0) > 0:
            mongo.db.movies.update_one(
                {"title": movie_title},
                {"$inc": {"copies": -1}},
            )

            rental = mongo.db.Rentals.find_one(
                {"movie": movie_title, "phoneno": phoneno}
            )

            if rental:
                mongo.db.Rentals.update_one(
                    {"_id": rental["_id"]},
                    {"$inc": {"copies": 1}},
                )
            else:
                mongo.db.Rentals.insert_one(
                    {"movie": movie_title, "phoneno": phoneno, "copies": 1}
                )

            msg = f"You rented: {movie['title']}."
            if _is_ajax_request():
                return _json_message(True, msg)
            return f"{msg}<br><a href='/'>Back to Homepage</a>"
        msg = "Sorry, no copies left!"
        if _is_ajax_request():
            return _json_message(False, msg, 400)
        return f"{msg}<br><a href='/'>Back to Homepage</a>"

    return f"""
        <h2>{escape(movie['title'])}</h2>
        <p>Year: {movie.get('year', 'N/A')}</p>
        <p>Copies available: {movie.get('copies', 0)}</p>
        <form action="/renting" method="POST">
            <input type="hidden" name="title" value="{escape(movie['title'])}"><br>
            <label for="phoneno">Phone Number:</label>
            <input type="text" name="phoneno" required><br><br>
            <input type="submit" value="Rent">
        </form>
    """


 
@app.route("/movies", methods=["GET"])
def list_movies():
    cursor = mongo.db.movies.find({}, {"title": 1}).sort("title", 1)
    movies = [{"id": str(doc["_id"]), "title": doc["title"]} for doc in cursor]
    return render_template("movies.html", movies=movies, query=None, search_type=None)


@app.route("/search")
def search():
    query = (request.args.get("query") or "").strip()
    if not query:
        return redirect(url_for("list_movies"))

    cursor = mongo.db.movies.find(
        {"title": {"$regex": query, "$options": "i"}},
        {"title": 1},
    ).sort("title", 1)
    movies = [{"id": str(doc["_id"]), "title": doc["title"]} for doc in cursor]
    return render_template("movies.html", movies=movies, query=query, search_type="title")


@app.route("/semantic_search")
def semantic_search():
    query = (request.args.get("query") or "").strip()
    if not query:
        return redirect(url_for("list_movies"))

    query_vector = embed_text(query)

    results = list(mongo.db.movies.aggregate([
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 100,
            "limit": 20
        }
    },
    {
        "$project": {
            "_id": 1,
            "title": 1,
            "year": 1,
            "description": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
    ]))

    movies = [
        {
            "id": str(r["_id"]),
            "title": r["title"],
            "description": r.get("description", ""),
            "score": r.get("score")
        }
        for r in results
    ]

    return render_template("movies.html", movies=movies, query=query, search_type="vibe")





@app.route("/movie/<movie_id>", methods=["GET"])
def show_movie(movie_id):
    if not ObjectId.is_valid(movie_id):
        return "Invalid movie id.", 400
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        return "Movie not found", 404
    t = escape(movie["title"])
    y = movie.get("year", "N/A")
    c = movie.get("copies", 0)
    mid = escape(movie_id)
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{t}</title></head>
<body>
  <h2>{t}</h2>
  <p>Year: {y}</p>
  <p>Copies available: {c}</p>
  <form id="rentForm" method="post">
    <button type="submit">Rent</button>
  </form>
  <p><a href="/movies">Back to list</a></p>
  <script>
    document.getElementById("rentForm").addEventListener("submit", async function (e) {{
      e.preventDefault();
      const res = await fetch("/rent/{mid}", {{
        method: "POST",
        headers: {{ "X-Requested-With": "XMLHttpRequest" }}
      }});
      let data = {{}};
      try {{ data = await res.json(); }} catch (x) {{}}
      alert(data.message || (res.ok ? "Done." : "Request failed."));
      if (res.ok && data.ok) window.location.href = "/movies";
    }});
  </script>
</body>
</html>"""



@app.route("/rent_profile")
def rent_profile():
    return render_template("renting.html", rentals=_rentals_for_template())


@app.route("/rent/<movie_id>", methods=["GET", "POST"])
def rent_movie(movie_id):
    if not ObjectId.is_valid(movie_id):
        if _is_ajax_request():
            return _json_message(False, "Invalid movie id.", 400)
        return "Invalid movie id.", 400

    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    rentals = _rentals_for_template()

    if request.method == "GET":
        if not movie:
            return "Movie not found.", 404
        return render_template("renting.html", rentals=rentals)

    if _is_ajax_request():
        if movie and movie.get("copies", 0) > 0:
            mongo.db.movies.update_one(
                {"_id": ObjectId(movie_id)},
                {"$inc": {"copies": -1}},
            )
            return _json_message(True, f"You rented: {movie['title']}.")
        if movie:
            return _json_message(False, "Sorry, no copies left!", 400)
        return _json_message(False, "Movie not found.", 404)

    if movie and movie.get("copies", 0) > 0:
        mongo.db.movies.update_one(
            {"_id": ObjectId(movie_id)},
            {"$inc": {"copies": -1}},
        )
        rentals = _rentals_for_template()
        return render_template("renting.html", rentals=rentals)
    if movie:
        return render_template("renting.html", rentals=rentals)
    return "Movie not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 9000)))

