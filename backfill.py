import os, time
from app import app, mongo
from llm import generate_movie_description
from embeddings import embed_text

with app.app_context():
    # Find movies with no description OR fallback description
    movies = list(mongo.db.movies.find({
        "$or": [
            {"description": {"$exists": False}},
            {"description": {"$regex": r"^\w.*\(\d{4}\)$"}}  # matches "Title (2010)" pattern
        ]
    }))

    print(f"Found {len(movies)} movies needing descriptions")

    for i, movie in enumerate(movies):
        title = movie.get("title", "")
        year  = movie.get("year")
        print(f"[{i+1}/{len(movies)}] {title}...")

        desc = generate_movie_description(title, year)
        if not desc:
            print(f"  Skipped (LLM failed)")
            continue

        vector = embed_text(desc)

        mongo.db.movies.update_one(
            {"_id": movie["_id"]},
            {"$set": {"description": desc, "embedding": vector}}
        )
        print(f"  Done")
        time.sleep(0.5)  # 0.5s delay to avoid rate limits

print("Done!")