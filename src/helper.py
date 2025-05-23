from langchain.document_loaders import JSONLoader, PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import jq
from langchain.embeddings import OpenAIEmbeddings


def load_json_directory(data):
    loader = DirectoryLoader(
        data,
        glob="*.json",
        loader_cls=JSONLoader,
        loader_kwargs={
            "jq_schema": ".[]",
            "content_key": "description",
            "text_content": True
        }
       
    )
    documents = loader.load()
    return documents



#Split the Data into Text Chunks
def text_split(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks



# Download the embeddings from OpenAI
def download_openai_embeddings():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  
    return embeddings