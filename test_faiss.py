from sentence_transformers import SentenceTransformer
import sqlite3
import faiss
import numpy as np

# Load the pre-trained Sentence-BERT model for embedding generation
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Connect to the SQLite database
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

# Query to fetch the captions
cursor.execute("SELECT id, caption FROM posts")
posts = cursor.fetchall()

# Extract captions and generate embeddings
captions = [post[1] for post in posts]
embeddings = model.encode(captions)

# Convert embeddings to numpy array and normalize for FAISS
embeddings = np.array(embeddings).astype('float32')
faiss.normalize_L2(embeddings)  # Normalize the embeddings

# Create a FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance metric

# Add embeddings to the FAISS index
index.add(embeddings)

# Save the FAISS index to disk
faiss.write_index(index, 'posts.index')

# Perform a similarity search with a query (for example, a random caption)
query_caption = "virtual fitness workout"
query_embedding = model.encode([query_caption]).astype('float32')
faiss.normalize_L2(query_embedding)

# Search for the top 3 similar posts
D, I = index.search(query_embedding, 3)

# Output the top 3 similar posts
print("Top 3 similar posts:")
for idx in I[0]:
    post_id = posts[idx][0]
    caption = posts[idx][1]
    print(f"Post ID: {post_id}, Caption: {caption}")

# Close the database connection
conn.close()