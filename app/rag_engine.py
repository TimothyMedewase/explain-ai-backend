from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import openai
import time
import logging
import os
import re
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conversation_histories = {}

# Define content type detection patterns
MATH_PATTERNS = [
    r"equation", r"formula", r"calculate", r"solve for", r"compute", 
    r"math problem", r"algebra", r"calculus", r"\bmath\b", 
    r"derivative", r"integral", r"theorem", r"\bproof\b"
]

LETTER_PATTERNS = [
    r"write a letter", r"formal letter", r"cover letter", 
    r"letter of \w+", r"business letter", r"email format"
]

def detect_content_type(query):
    """Detect the type of content being requested based on query patterns"""
    query = query.lower()
    
    # Check for math content
    for pattern in MATH_PATTERNS:
        if re.search(pattern, query):
            return "math"
            
    # Check for letter content
    for pattern in LETTER_PATTERNS:
        if re.search(pattern, query):
            return "letter"
    
    # Default content type
    return "general"

def get_formatting_instructions(content_type):
    """Get specific formatting instructions based on content type"""
    if content_type == "math":
        return """
        For mathematical content:
        1. Format all equations using LaTeX syntax: Enclose equations in $...$ for inline or $$...$$ for display equations
        2. Use proper mathematical notation (e.g., \\frac{}{} for fractions, ^{} for exponents)
        3. For complex derivations, show step-by-step work
        4. Explain the meaning of variables and symbols used
        """
    
    elif content_type == "letter":
        return """
        For letter content:
        1. Use proper letter format with date, address, salutation, and closing
        2. Organize content into clear paragraphs with appropriate spacing
        3. Maintain a formal tone unless otherwise specified
        4. Include all necessary components (sender info, recipient info, signature)
        """
    
    # Default formatting instructions
    return """
    For general content:
    1. Use clear paragraph structure with headers when appropriate
    2. Provide concise, well-organized information
    3. Use bullet points or numbered lists for steps or multiple items
    4. Include relevant examples or references from the source material
    """

def process_user_query(query: str, documents: list[str], conversation_id: str = None) -> dict:
    try:
        if not conversation_id:
            conversation_id = str(uuid4())
        
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        memory = conversation_histories[conversation_id]
        
        # Detect content type and get appropriate formatting instructions
        content_type = detect_content_type(query)
        formatting_instructions = get_formatting_instructions(content_type)
        
        # Create a prompt template that includes formatting instructions AND the context variable
        prompt_template = f"""
        You're analyzing documents to answer the user's question.
        
        {formatting_instructions}
        
        Based on the following conversation history and the user's new question, provide a well-formatted response 
        using the guidelines above.
        
        Chat History: {{chat_history}}
        Context: {{context}}
        Question: {{question}}
        
        Answer:
        """
        
        # Rest of the document processing code
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
                
        # Create the custom prompt with the context variable included
        custom_prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["chat_history", "question", "context"]
        )
        
        # Use the custom prompt in the chain
        qa = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0, model="gpt-4"),
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": custom_prompt}
        )
        
        result = qa.invoke({"question": query})
        
        return {
            "answer": result["answer"],
            "conversation_id": conversation_id,
            "content_type": content_type  # Return the detected content type for frontend rendering
        }
    except Exception as e:
        logger.error(f"Error in process_user_query: {str(e)}")
        raise
