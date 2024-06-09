from typing import List
import streamlit as st
import os, shutil
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv

load_dotenv()

llamaparser_api_key = os.getenv("LLAMA_CLOUD_API_KEY")

def load_data():
    parser = LlamaParse(
        api_key = llamaparser_api_key,
        result_type="markdown")
    file_extractor =  {".pdf": parser}
    reader = SimpleDirectoryReader(input_dir="src/data", file_extractor=file_extractor)
    docs = reader.load_data()
    return docs


def RAG(_config, _docs):
    service_context = ServiceContext.from_defaults(
        llm=OpenAI(
            model=_config.gpt_model,
            temperature=_config.temperature,
            max_tokens=_config.max_tokens,
            system_prompt=_config.llm_system_role,
        ),
        chunk_size=_config.chunk_size,
    )
    index = VectorStoreIndex.from_documents(_docs, service_context=service_context)
    return index


def delete_data():
    print("Cleaning the data folder")
    folder = "src/data"
    for filename in os.listdir(folder):
        if filename != ".gitignore":
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
