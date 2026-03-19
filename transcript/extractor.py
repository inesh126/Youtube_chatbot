from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL")

def get_transcript(url):
    video_id = extract_video_id(url)

 
    transcript = YouTubeTranscriptApi().fetch(video_id)

    texts = []
    for t in transcript:
        texts.append({
            "text": t.text,     
            "start": t.start
        })

    return texts