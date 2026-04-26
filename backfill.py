import os
from app import app, mongo
from embeddings import embed_text

with app.app_context():
    movies = list(mongo.db.movies.find({"embedding": {"$exists": False}}))
    print(f"Found {len(movies)} movies without embeddings")

    for i, movie in enumerate(movies):
        title = movie.get("title", "")
        year = movie.get("year", "")
        text = f"{title} {year}".strip()

        vector = embed_text(text)

        mongo.db.movies.update_one(
            {"_id": movie["_id"]},
            {"$set": {"embedding": vector}}
        )

        if i % 100 == 0:
            print(f"Progress: {i}/{len(movies)}")

print("Backfill complete!")
