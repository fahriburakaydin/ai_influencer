import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3

# Load the SentenceTransformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to fetch captions from the database
def fetch_post_captions(db_path='posts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, caption FROM posts")  # Use 'id' instead of 'post_id'
    posts = cursor.fetchall()
    conn.close()
    return posts

# Function to create and save the FAISS index
def create_and_save_faiss_index(posts, index_file='posts.index'):
    # Extract captions from posts
    captions = [post[1] for post in posts]
    
    # Generate embeddings for captions
    embeddings = model.encode(captions)
    
    # Create the FAISS index
    dim = embeddings.shape[1]  # Get the dimensionality of the embeddings
    index = faiss.IndexFlatL2(dim)  # Use L2 distance for similarity search
    
    # Add the embeddings to the index
    index.add(np.array(embeddings, dtype=np.float32))
    
    # Save the index
    faiss.write_index(index, index_file)
    print(f"Faiss index saved to {index_file}")

# Function to load the FAISS index
def load_faiss_index(index_file='posts.index'):
    return faiss.read_index(index_file)

# Function to query the FAISS index
def query_faiss_index(query_text, index, top_k=3):
    query_embedding = model.encode([query_text])
    query_embedding = np.array(query_embedding, dtype=np.float32)
    
    # Perform the search
    D, I = index.search(query_embedding, top_k)
    
    return I[0], D[0]  # Return the indices and distances of the top_k results

# Main function
def main():
    # Fetch the posts from the database
    posts = fetch_post_captions()
    
    # Create and save the FAISS index (this needs to be run only once)
    create_and_save_faiss_index(posts)
    
    # Load the FAISS index
    index = load_faiss_index()
    
    # Query the FAISS index with a sample query
    query_text = "virtual fitness workout"
    indices, distances = query_faiss_index(query_text, index)
    
    print(f"Top {len(indices)} similar posts for the query '{query_text}':")
    for idx, dist in zip(indices, distances):
        post_id, caption = posts[idx]
        print(f"Post ID: {post_id}, Caption: {caption}, Distance: {dist}")

if __name__ == '__main__':
    main()