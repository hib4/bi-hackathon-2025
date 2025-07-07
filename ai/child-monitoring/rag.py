from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import shutil
import json

class ChildMonitoringRAG:
    def __init__(
        self, data_dir: str, persist_directory: str, model: str = "text-embedding-3-small"
    ):
        self.data_dir = data_dir
        self.persist_dircetory = persist_directory
        self.model = model
        
        # Initialize RAG components
        self.embeddings = OpenAIEmbeddings(model=model)
        self.vectorstore = None
        self.retriever = None
        
