from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_transcript(transcript):
    full_text = " ".join([t["text"] for t in transcript])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(full_text)
    return chunks