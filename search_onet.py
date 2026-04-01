import chromadb
import ollama
import mysql.connector


client = ollama.Client(host="http://localhost:11436")
#connect to chromadb
chroma_client = chromadb.HttpClient(host="localhost", port=8001)
collection = chroma_client.get_collection(name="onet_semantic_index")

#connect mysql
db_connection = mysql.connector.connect(
    host="localhost",
    port="3307",
    user="root",
    password="P@ssW0rd!",
    database="onet_db"
)

#cursor is the point to that iterates through the db rows 
#dicitonary=True makes the data retrun back as a {col: value} pair
cursor = db_connection.cursor(dictionary=True)

def search_onet(user_query):

    print(f"\nSearching for: {user_query}")

    #generate the vector embedding for the user query
    response = ollama.embeddings(model="nomic-embed-text", prompt=user_query)
    query_vector_data = response['embedding']

    #search the collection for the most similar vectors
    results = collection.query(
        query_embeddings=[query_vector_data],
        n_results=5
    )

    print("\n--- RESULTS FOUND ---")
    for i in range(len(results['ids'][0])):
        soc_code = results['ids'][0][i]
        title = results['metadatas'][0][i]['title']
        
        # STEP C: Go to MySQL to get specific 'Tools' for this SOC code
        # This is where the "Relational" part happens!
        sql = "SELECT example FROM technology_skills WHERE onetsoc_code = %s LIMIT 3"
        cursor.execute(sql, (soc_code,))
        tools = cursor.fetchall()
        tool_names = [t['example'] for t in tools]

        print(f"\n{i+1}. {title} (Code: {soc_code})")
        print(f"   Common Tools: {', '.join(tool_names) if tool_names else 'N/A'}")

def generate_skills_manifest(job_title, company_context):
    # 1. Get standard O*NET skills from MySQL
    standard_skills = query_mysql(job_title)
    
    # 2. Get company-specific "secret sauce" from ChromaDB
    company_specifics = chroma_collection.query(query_texts=[job_title])
    
    # 3. Use Ollama to merge them into a single 'Resume Killer' document
    prompt = f"Combine these standard skills {standard_skills} with these company requirements {company_specifics}..."
    return client.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])

#test
query = input("\nDescribe your dream job or interests: ")
search_onet(query)

cursor.close()
db_connection.close()