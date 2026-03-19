import streamlit as st

from pipeline import process_video, ask_question
from transcript.extractor import extract_video_id

MAX_QUESTION_LENGTH = 400
BLOCKED_PATTERNS = (
    "reveal system prompt",
    "show hidden prompt",
)
SUGGESTED_QUESTIONS = (
    "Summarize the main points of this video.",
    "What are the key takeaways?",
    "What examples or case studies were mentioned?",
    "What does the speaker say about the main topic?",
)


def validate_question(question):
    cleaned_question = question.strip()
    if not cleaned_question:
        return False, "Question cannot be empty."
    if len(cleaned_question) > MAX_QUESTION_LENGTH:
        return False, f"Question is too long. Keep it under {MAX_QUESTION_LENGTH} characters."

    lowered_question = cleaned_question.lower()
    if any(pattern in lowered_question for pattern in BLOCKED_PATTERNS):
        return False, "That request is blocked."

    return True, cleaned_question


def initialize_session_state():
    defaults = {
        "collection": None,
        "chat_history": [],
        "video_url": "",
        "video_id": None,
        "selected_prompt": SUGGESTED_QUESTIONS[0],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_video_session():
    st.session_state.collection = None
    st.session_state.chat_history = []
    st.session_state.video_id = None


def reset_video_and_input():
    reset_video_session()
    st.session_state.video_url = ""


def process_current_video():
    video_url = st.session_state.video_url.strip()
    if not video_url:
        st.error("Enter a YouTube URL first.")
        return

    try:
        video_id = extract_video_id(video_url)
    except ValueError as exc:
        reset_video_session()
        st.error(str(exc))
        return

    with st.spinner("Processing transcript and building retrieval context..."):
        collection = process_video(video_url)

    st.session_state.collection = collection
    st.session_state.chat_history = []
    st.session_state.video_id = video_id
    st.success("Video processed. You can start chatting.")


def clear_chat_memory():
    st.session_state.chat_history = []
    st.toast("Session memory cleared.")


def render_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(245, 93, 62, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(255, 205, 86, 0.15), transparent 24%),
                linear-gradient(180deg, #fff8f0 0%, #f6f2eb 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1180px;
        }
        .hero-card {
            padding: 1.6rem 1.7rem;
            border-radius: 22px;
            background:
                radial-gradient(circle at top right, rgba(255, 255, 255, 0.14), transparent 24%),
                linear-gradient(135deg, #0f0f0f 0%, #1f1f1f 42%, #ff0033 100%);
            color: #ffffff;
            box-shadow: 0 24px 60px rgba(200, 0, 0, 0.22);
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 0.35rem;
        }
        .hero-copy {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.86);
            line-height: 1.55;
        }
        .status-card {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(102, 78, 57, 0.12);
            box-shadow: 0 16px 32px rgba(44, 33, 23, 0.08);
            margin-bottom: 0.9rem;
        }
        .status-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #8a6a50;
            margin-bottom: 0.4rem;
        }
        .status-value {
            font-size: 1rem;
            font-weight: 600;
            color: #2c241d;
        }
        .pill-row {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.7rem;
        }
        .pill {
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #f3e4d3;
            color: #7b5535;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #2c241d;
            margin-bottom: 0.45rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fffdf8 0%, #f4ecdf 100%);
            border-right: 1px solid rgba(102, 78, 57, 0.12);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">YouTube Chatbot</div>
            <div class="hero-copy">
                Process a video transcript, ask follow-up questions, and keep short-term memory inside the current session only.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("## Control Panel")
        st.text_input(
            "YouTube URL",
            key="video_url",
            placeholder="https://www.youtube.com/watch?v=...",
        )
        st.button("Process Video", use_container_width=True, on_click=process_current_video)

        col1, col2 = st.columns(2)
        with col1:
            st.button("Clear Chat", use_container_width=True, on_click=clear_chat_memory)
        with col2:
            st.button("Reset Video", use_container_width=True, on_click=reset_video_and_input)

        st.markdown("---")
        st.markdown("### Starter Questions")
        selected_prompt = st.selectbox(
            "Pick a prompt",
            SUGGESTED_QUESTIONS,
            key="selected_prompt",
        )
        if st.button("Use Prompt in Chat", use_container_width=True):
            st.session_state.chat_input_prefill = selected_prompt
            st.rerun()

        st.markdown("---")
        st.caption("Session memory lives only in the current Streamlit session.")


def render_status_panel():
    video_status = "Ready" if st.session_state.collection else "Waiting for video"
    video_id = st.session_state.video_id or "Not processed yet"
    turn_count = len(st.session_state.chat_history) // 2

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Session Status</div>
                <div class="status-value">{video_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Video ID</div>
                <div class="status-value">{video_id}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Conversation Turns</div>
                <div class="status-value">{turn_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="pill-row">
            <div class="pill">Transcript-based answers</div>
            <div class="pill">Session memory only</div>
            <div class="pill">Basic guardrails enabled</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def submit_question(question):
    is_valid, result = validate_question(question)
    if not is_valid:
        st.error(result)
        return

    cleaned_question = result
    with st.spinner("Searching the transcript and composing an answer..."):
        answer = ask_question(
            st.session_state.collection,
            cleaned_question,
            st.session_state.chat_history,
        )

    st.session_state.chat_history.append({"role": "user", "content": cleaned_question})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})


def render_chat_area():
    st.markdown('<div class="section-title">Conversation</div>', unsafe_allow_html=True)

    if not st.session_state.collection:
        st.info("Process a YouTube video from the sidebar to unlock chat, memory, and suggested prompts.")
        return

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div class="status-card">
                Ask about summaries, claims, examples, steps, or anything specifically mentioned in the transcript.
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    pending_prompt = st.session_state.pop("chat_input_prefill", None)
    if pending_prompt:
        st.caption(f"Suggested prompt ready: {pending_prompt}")

    question = st.chat_input("Ask something about the current video")
    if question is None and pending_prompt:
        question = pending_prompt

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        submit_question(question)
        st.rerun()


st.set_page_config(
    page_title="YouTube Chatbot",
    page_icon="YT",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
render_styles()
render_sidebar()
render_header()
render_status_panel()
render_chat_area()
