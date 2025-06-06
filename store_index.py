from src.helper import load_json_directory, text_split, download_openai_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


extracted_data=load_json_directory(data='PreprocessedData')
text_chunks=text_split(extracted_data)
embeddings = download_openai_embeddings()


pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "raterbot"


pc.create_index(
    name=index_name,
    dimension=3072, 
    metric="cosine", 
    spec=ServerlessSpec(
        cloud="aws", 
        region="us-east-1"
    ) 
) 

# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings, 
)