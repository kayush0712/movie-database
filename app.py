from flask import Flask, request, jsonify,render_template
from flask_pymongo import PyMongo
from bson import ObjectId
import os
from bson.objectid import ObjectId

app = Flask(__name__)


app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb+srv://kayush0712:Ayush%40123@demo-cluster.s0jc1hf.mongodb.net/sample_mflix?retryWrites=true&w=majority&appName=demo-cluster")
mongo = PyMongo(app)

@app.route("/")
def index():
    movies = list(mongo.db.movies.find({}, {"_id": 0, "title": 1}))
    return render_template("index.html", movies=movies)


@app.route("/profile")
def profile():
    return render_template("profile.html")


    

@app.route("/insert_movie", methods=["POST"])
def insert_movie():
    title = request.form.get('title')
    year = request.form.get('year')
      

    if title and year :
        mongo.db.movies.insert_one({
            'title': title,
            'year': int(year),
            
        })
        return f"Inserted movie: {title} ({year})"
    return "Missing title or year"


@app.route("/update_movie", methods=["POST"])
def update_movie():

    title = request.form.get('title')
    year = request.form.get('year')
    

    if title and year :
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

@app.route("/renting", methods=["GET", "POST"])
def rent_movie_form():
    movie_title = request.form.get('title') if request.method == "POST" else request.args.get('title')

    if not movie_title:
        return "No movie title provided."

    movie = mongo.db.movies.find_one({"title": movie_title})
    
    if not movie:
        return "Movie not found."

    if request.method == "POST":
        phoneno = request.form.get('phoneno')

        if movie.get('copies', 0) > 0:
            # Reduce movie copy count
            mongo.db.movies.update_one(
                {"title": movie_title},
                {"$inc": {"copies": -1}}
            )

            # 👉 Check if this user already rented the same movie
            rental = mongo.db.Rentals.find_one({
                "movie": movie_title,
                "phoneno": phoneno
            })

            if rental:
                # Increment copies field if exists
                mongo.db.Rentals.update_one(
                    {"_id": rental["_id"]},
                    {"$inc": {"copies": 1}}
                )
            else:
                # First time renting this movie, insert with 1 copy
                mongo.db.Rentals.insert_one({
                    "movie": movie_title,
                    "phoneno": phoneno,
                    "copies": 1
                })

            return f"You rented: {movie['title']}<br><a href='/'>Back to Homepage</a>"
        else:
            return "Sorry, no copies left!<br><a href='/'>Back to Homepage</a>"

    # If GET, show the rental form
    return f""" 
        <h2>{movie['title']}</h2>
        <p>Year: {movie.get('year', 'N/A')}</p>
        <p>Copies available: {movie.get('copies', 0)}</p>
        <form action="/renting" method="POST">
            <input type="hidden" name="title" value="{movie['title']}"><br>
            <label for="phoneno">Phone Number:</label>
            <input type="text" name="phoneno" required><br><br>
            <input type="submit" value="Rent">
        </form>
    """


 
@app.route("/movies", methods=["GET"])
def list_movies():
    movies = mongo.db.movies.find({}, {"title": 1})
    output = """
        <form action="/search" method="GET">
            <input type="text" name="query" placeholder="Search movie title">
            <input type="submit" value="Search">
        </form>
        <hr>
    """
    for movie in movies:
        movie_id = str(movie["_id"])
        output += f'<a href="/movie/{movie_id}">{movie["title"]}</a><br>'
    return output





@app.route("/movie/<movie_id>", methods=["GET"])
def show_movie(movie_id):
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie:
        return f"""
        <h2>{movie['title']}</h2>
        <p>Year: {movie.get('year', 'N/A')}</p>
        <p>Copies available: {movie.get('copies', 0)}</p>
        <form action="/rent/{movie_id}" method="POST">
            <input type="submit" value="Rent">
        </form>
        """
    else:
        return "Movie not found"

@app.route("/search")
def search():
    query = request.args.get("query")
    if query:
        results = mongo.db.movies.find({"title": {"$regex": query, "$options": "i"}})
        output = f"<h3>Search results for: {query}</h3>"
        for movie in results:
            movie_id = str(movie["_id"])
            output += f'<a href="/movie/{movie_id}">{movie["title"]}</a><br>'
        return output
    return "Please enter a search query."

@app.route("/rent_profile")
def rent_profile():
    rentals = mongo.db.Rentals.find({},{"_id": 0, "movie": 1,"phoneno": 1,"copies": 1})
    rentals = list(rentals)
    
    output = "<h2>Rental Profile</h2>"
    for rental in rentals:
        print(rental['copies'])
        output += f"<p>Movie: {rental['movie']} <br>Phone No: {rental['phoneno']}<br> Copies: {rental['copies']}</p>"
    return output

@app.route("/rent/<movie_id>", methods=["POST"])
def rent_movie(movie_id):
    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie and movie.get('copies', 0) > 0:
        mongo.db.movies.update_one(
            {"_id": ObjectId(movie_id)},
            {"$inc": {"copies": -1}}  # Decrease copies by 1
        )
        return f"You rented: {movie['title']}<br><a href='/movie/{movie_id}'>Back</a>"
    elif movie:
        return f"Sorry, no copies left!<br><a href='/movie/{movie_id}'>Back</a>"
    else:
        return "Movie not found."


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

