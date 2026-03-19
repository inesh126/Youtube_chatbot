import chromadb

client = chromadb.Client()

def create_collection(name="youtube_rag"):
    return client.get_or_create_collection(name)

def add_chunks(collection, chunks):
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[str(i)]
        )

def query_collection(collection, query, n_results=3):
    return collection.query(
        query_texts=[query],
        n_results=n_results
    )