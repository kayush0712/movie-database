from pymongo import MongoClient

# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://kayush0712:Ayush%40123@demo-cluster.s0jc1hf.mongodb.net/?retryWrites=true&w=majority&appName=demo-cluster")
db = client['sample_mflix']  # Use your database name
collection = db['movies']      # Use your collection name

# 2. Add 'copies' field with a default value (e.g., 0) to all documents
collection.update_many(
    {},
    {
        "$set": {"copies": int(10)}  # set default copies
    }
)

print("Copies field added to all documents.")
