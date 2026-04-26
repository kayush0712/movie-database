# 🎬 Movie Database

A full-stack movie rental web app with AI-powered semantic search — find movies by vibe, not just title.

🔗 **[Live Demo](https://movie-database-c21r.onrender.com)**

---

## Overview

Movie Database is a cinema management dashboard built with Flask and MongoDB Atlas. Beyond standard CRUD operations, it features a **vector search engine** that lets users search for movies using natural language — describe a mood, theme, or feeling and get semantically ranked results.

New movies added to the database are automatically enriched with AI-generated descriptions via an LLM, which are then converted into 384-dimensional vector embeddings and stored in MongoDB Atlas for cosine similarity search.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MongoDB Atlas |
| Vector Search | MongoDB Atlas Vector Search |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) |
| LLM | OpenRouter API |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |
| Deployment | Render |
