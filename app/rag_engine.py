from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import openai
import time
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_user_query(query: str, documents: list[str]) -> str:
    try:
       
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = []
        for doc in documents:
            chunks.extend(splitter.split_text(doc))
        
     
        max_retries = 3
        retry_delay = 2  
        for attempt in range(max_retries):
            try:
                embeddings = OpenAIEmbeddings()
                
                vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
                retriever = vectorstore.as_retriever()
                break
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2 
                else:
                    logger.error("Max retries reached for OpenAI API")
                    raise Exception("OpenAI API rate limit exceeded. Please try again later.")
            except Exception as e:
                logger.error(f"Error creating embeddings: {str(e)}")
                raise

        
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=retriever
        )
        
      
        result = qa.invoke(query)
        return result
    except Exception as e:
        logger.error(f"Error in process_user_query: {str(e)}")
        raise
