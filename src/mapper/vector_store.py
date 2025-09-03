from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class VectorstoreBuilder:
    def __init__(self, embeddings_model: str):
        self.embeddings_model = embeddings_model

    def create_faiss_index(self, documents):
        embeddings = HuggingFaceEmbeddings(model_name=self.embeddings_model)
        return FAISS.from_documents(documents, embeddings)