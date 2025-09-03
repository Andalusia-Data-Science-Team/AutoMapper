from fireworks_llm import get_fireworks_llm
from langchain.chains import RetrievalQA

class RAGChainFactory:
    def create_rag_chain(self, vectorstore, prompt_template):
        llm = get_fireworks_llm()
        return RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
    
