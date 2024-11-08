import uuid
import os
from tqdm import tqdm
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document
from langchain.storage import LocalFileStore

class VectorStore:
    def __init__(self, df, persist_directory="./data/chroma_db"):
        self.df = df
        self.persist_directory = persist_directory
        self.vectorstore = Chroma(
            collection_name="PAS_codebase", 
            embedding_function=HuggingFaceEmbeddings(),
            persist_directory=persist_directory
        )
        self.docstore = LocalFileStore(f"{self.persist_directory}/docstore")
        self.id_key = "doc_id"
        self.retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            id_key=self.id_key,
        )
        os.makedirs(self.persist_directory, exist_ok=True)

    def prepare_data(self):
        code = self.df['Content'].tolist()
        doc_ids = [str(uuid.uuid4()) for _ in code]
        code_docs = [
            Document(page_content=s, metadata={self.id_key: doc_ids[i]})
            for i, s in enumerate(code)
        ]
        return doc_ids, code, code_docs

    def add_to_stores(self):
        doc_ids, code, code_docs = self.prepare_data()
        code_store_data = [
            (doc_id, doc_content.encode('utf-8'))  # Convert to bytes
            for doc_id, doc_content in zip(doc_ids, code)
        ]
        for item in code_store_data:
            self.retriever.docstore.mset([item])
        for doc in tqdm(code_docs, desc="Adding to Vectorstore"):
            self.retriever.vectorstore.add_documents([doc])

    def get_relevant_documents(self, query, limit=30):
        raw_docs = self.retriever.get_relevant_documents(query, limit=limit)
        
        decoded_docs = []
        for doc in raw_docs:
            if isinstance(doc, bytes):
                decoded_content = doc.decode('utf-8')
                decoded_doc = Document(page_content=decoded_content)
            elif isinstance(doc, Document):
                if isinstance(doc.page_content, bytes):
                    decoded_content = doc.page_content.decode('utf-8')
                    decoded_doc = Document(page_content=decoded_content, metadata=doc.metadata)
                else:
                    decoded_doc = doc
            else:
                # Handle unexpected types
                continue
            decoded_docs.append(decoded_doc)
        return decoded_docs
