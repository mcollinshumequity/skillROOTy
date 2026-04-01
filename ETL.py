#before your run
#pull model -> ollama pull nomic-embed-text
#installl python packages -> pip install mysql-connector-python chromadb ollama
#check docker is running -> docker ps both mysql(onet_db) and chromadb(chroma)

import mysql.connector # Connect to MySQL
import chromadb # Connect to ChromaDB
import ollama # Connect to Ollama


# Connect to the DBs
# Connect to mysql onet_db
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    port="3307",
    user="root",
    password="P@ssW0rd!",
    database="onet_db"
)

# cursor is the point to that iterates through the db rows 
# dicitonary=True makes the data retrun back as a {col: value} pair
cursor = db_connection.cursor(dictionary=True)

#connect to chromadb -> vector database
chroma_client = chromadb.HttpClient(host="localhost", port="8001")

#collection is like a table in SQL -> where we store our vectors
#if the collection doesn't exist, Chroma will create it
collection = chroma_client.get_or_create_collection(name="onet_semantic_index")

# Extract the data

print("Extracting data from MySQL...")

# SQL query to get the data
query = "SELECT onetsoc_code, title, description FROM occupation_data"
cursor.execute(query)
all_jobs = cursor.fetchall()


#Embedding & loading
print(f"Found {len(all_jobs)} occupations.")

for job in all_jobs:
    
    #[1] prep the text for the AI
    #combind title and description so AI knows what the job is called
    text_to_embed = f"Title: {job['title']}\nDescription: {job['description']}"

    #[2] Generate the vector embedding
    #ollama.embed takes the text and turns it into a list of numbers (vector)
    #The vector represents the "meaning" of the text
    # This turns our sentence into a list of ~768 numbers.
    embedding_response = ollama.embeddings(model="nomic-embed-text", prompt=text_to_embed)
    vector_data = embedding_response['embedding']

    #[3] Load into ChromaDB
    collection.add(
        ids=[job['onetsoc_code']],
        embeddings=[vector_data],
        documents=[text_to_embed],
        metadatas=[{"title": job['title'], "soc_code": job['onetsoc_code']}]
    )

    print(f"Vectorized: {job['title']}")

#[4] Clean up!
cursor.close()
db_connection.close()
print("ETL Process Completed!")