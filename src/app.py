import streamlit as st
from streamlit_chat import message
from PIL import Image
from utils.load_config import LoadConfig
from utils.app_utils import load_data, RAG, delete_data
import subprocess
import os


APPCFG = LoadConfig()

# ===================================
# Setting page title and header
# ===================================
im = Image.open("images/arXiv.png")
os.environ["OPENAI_API_KEY"] = st.secrets["openai_key"]

st.set_page_config(page_title="Senku-Bot", page_icon=im, layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Senku-Bot (Scientific Assistant)</h1>",
    unsafe_allow_html=True,
)
st.divider()
st.markdown(
        "<center><i>Hello! I'm Senku-Bot, your assistant for scientific explanations and relevant papers. Feel free to ask me anything about science, and I'll do my best to provide you with clear and concise answers, along with any relevant research papers that might help further your understanding. Let's explore the wonders of science together! If you have any questions, just ask.</center>",
        unsafe_allow_html=True,
    )
st.divider()

def message(text, is_user):
    if is_user:
        # User message
        st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <img src="https://anhanime.com/wp-content/uploads/2022/10/A%CC%89nh-Senku-14.jpg" alt="Avatar" style="border-radius: 50%; width: 40px; height: 40px;">
                <p style="margin-left: 10px;">{text}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Bot message
        st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQvvEzpnAIacHuu7jPDRorH594FXfylOfi_Lg&usqp=CAU" alt="Avatar" style="border-radius: 50%; width: 40px; height: 40px;">
                <p style="margin-left: 10px;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

# ===================================
# Initialise session state variables
# ===================================
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

# ==================================
# Sidebar:
# ==================================
counter_placeholder = st.sidebar.empty()
with st.sidebar:
    st.markdown(
        "<h3 style='text-align: center;'>Ask anything you need to brush up on!</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<center><b>Example: </b></center>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<center><i>What is GPT4?</i></center>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<center><i>Explain me Mixture of Models (MoE)</i></center>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<center><i>How does RAG works?</i></center>",
        unsafe_allow_html=True,
    )
    # st.sidebar.title("An agent that read and summarizethe the news for you")
    st.sidebar.image("images/arXiv.png", use_column_width=True)
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    st.markdown(
    "<a style='display: block; text-align: center;' href='https://www.linkedin.com/in/nttsc207/' target='_blank'> Thai Thong Nguyen</a>",
    unsafe_allow_html=True,
)
# ==================================
# Reset everything (Clear button)
if clear_button:
    st.session_state["generated"] = []
    st.session_state["past"] = []
    delete_data()

response_container = st.container()  # container for message display

if query := st.chat_input(
    "What do you need to know? I will explain it and point you out interesting readings."
):
    st.session_state["past"].append(query)
    try:
        with st.spinner("Please wait for browsing the best papers..."):
            process = subprocess.Popen(
                f"python src/utils/arxiv_scraper.py --query \"{query}\" --numresults {APPCFG.articles_to_search}",
                shell=True,
            )
            out, err = process.communicate()
            errcode = process.returncode

        with st.spinner("Reading them..."):
            data = load_data()
            index = RAG(APPCFG, _docs=data)
            query_engine = index.as_query_engine(
                response_mode="tree_summarize",
                verbose=True,
                similarity_top_k=APPCFG.similarity_top_k,
            )
        with st.spinner("Thinking..."):
            response = query_engine.query(query + APPCFG.llm_format_output)

        st.session_state["generated"].append(response.response)
        del index
        del query_engine

        with response_container:
            for i in range(len(st.session_state["generated"])):
                message(st.session_state["past"][i], is_user=True)

                message(st.session_state["generated"][i], is_user=False)

    except Exception as e:
        print(e)
        st.session_state["generated"].append(
            "An error occured with the paper search, please modify your query."
        )
