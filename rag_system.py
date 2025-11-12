import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class SimpleRAG:
    def __init__(self):
        # Priority: Streamlit secrets first, then .env file
        api_key = None
        
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
                st.success("✅ Using API key from Streamlit secrets")
        except:
            pass
            
        # Fall back to .env file
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and not api_key.startswith("your_actual"):
                st.info("ℹ️ Using API key from .env file")
        
        # Validate the key
        if not api_key or api_key.startswith("your_actual"):
            st.error("""
            ❌ OpenAI API key not configured properly.
            
            Please make sure you've added your real API key to Streamlit Secrets:
            1. Go to your app dashboard
            2. Click '⋮' → 'Settings' → 'Secrets'  
            3. Add: OPENAI_API_KEY = "your-real-key-here"
            4. Save and refresh this app
            """)
            self.client = None
            return
            
        self.client = OpenAI(api_key=api_key)
        self.current_document = ""
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
    
    def query(self, question, n_results=3):
        if not self.client:
            return "OpenAI client not configured. Please check your API key in Streamlit secrets."
            
        try:
            if not self.current_document:
                return "Please upload a document first."
            
            prompt = f"""Based on the following study materials, answer the question.

Study Materials:
{self.current_document}

Question: {question}

Answer:"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant. Answer based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"API Error: {str(e)}"
