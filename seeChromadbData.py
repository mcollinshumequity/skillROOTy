import chromadb

#connect to the chromadb container in docker
chroma_client = chromadb.HttpClient(host="localhost", port=8001)

#grab the collection created from ETL.py
collection = chroma_client.get_collection(name="onet_semantic_index")

#count how many items are in the collection
count = collection.count()
print(f"There are {count} items in the collection.")

#Peek a the the first item
peek = collection.peek(1)
print(f"Sample Metadata: {peek['metadatas']}")