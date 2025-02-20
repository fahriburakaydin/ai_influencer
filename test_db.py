import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('posts.db')  # Ensure the path is correct

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Query to fetch the post ID and caption
cursor.execute("SELECT id, caption FROM posts")

# Fetch all rows from the query
posts = cursor.fetchall()

# Print the results
for post in posts:
    print(f"Post ID: {post[0]}, Caption: {post[1]}")

# Close the connection
conn.close()
