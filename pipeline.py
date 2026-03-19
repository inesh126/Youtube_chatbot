from transcript.extractor import get_transcript
from chunking.splitter import split_transcript
from memory.vectordb import create_collection, add_chunks, query_collection
from llm.model import generate_answer

MAX_CONTEXT_CHUNKS = 3
MAX_CONTEXT_CHARACTERS = 4000
MAX_RETRIEVAL_DISTANCE = 2.2
NO_EVIDENCE_MESSAGE = "I couldn't find this clearly in the video."


def build_context(results):
    documents = results.get("documents", [[]])
    distances = results.get("distances", [[]])

    docs = documents[0] if documents else []
    doc_distances = distances[0] if distances else []

    filtered_docs = []
    for index, doc in enumerate(docs):
        distance = doc_distances[index] if index < len(doc_distances) else None
        if distance is None or distance <= MAX_RETRIEVAL_DISTANCE:
            filtered_docs.append(doc)

    if not filtered_docs:
        filtered_docs = docs[:MAX_CONTEXT_CHUNKS]

    if not filtered_docs:
        return None

    return " ".join(filtered_docs[:MAX_CONTEXT_CHUNKS])[:MAX_CONTEXT_CHARACTERS]


def process_video(url):
    transcript = get_transcript(url)
    chunks = split_transcript(transcript)

    collection = create_collection()
    add_chunks(collection, chunks)

    return collection

def ask_question(collection, question, chat_history=None):
    results = query_collection(collection, question, n_results=5)
    context = build_context(results)
    if not context:
        return NO_EVIDENCE_MESSAGE

    answer = generate_answer(context, question, chat_history or [])
    return answer
