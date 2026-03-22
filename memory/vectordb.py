import chromadb
from chromadb.utils import embedding_functions

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

client = chromadb.Client()
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME
)

def create_collection(name="youtube_rag"):
    try:
        client.delete_collection(name)
    except Exception:
        pass

    return client.get_or_create_collection(
        name=name,
        embedding_function=embedding_function,
    )

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
