import os
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()

class SimpleRAG:
    def __init__(self):
        # Updated OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Updated ChromaDB client (new syntax)
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection("study_docs")
    
    def chunk_text(self, text, chunk_size=1000):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        return chunks
    
    def add_document(self, text, doc_id):
        if not text or text == "Unsupported file type":
            return
            
        chunks = self.chunk_text(text)
        
        # Add to ChromaDB
        self.collection.add(
            documents=chunks,
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
        )
    
    def query(self, question, n_results=3):
        try:
            # Search for relevant chunks
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results
            )
            
            # Handle case where no results are found
            if not results['documents'] or not results['documents'][0]:
                return "No relevant information found in your documents. Try uploading more content or asking a different question."
            
            context = "\n\n".join(results['documents'][0])
            
            # Create prompt with context
            prompt = f"""Based on the following context from study materials, answer the question.

Context:
{context}

Question: {question}

Answer:"""
            
            # Get answer from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant. Answer questions based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}. Please check your OpenAI API key in the .env file."
