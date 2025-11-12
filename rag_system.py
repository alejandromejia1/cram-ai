import os
from openai import OpenAI
import streamlit as st

class SimpleRAG:
    def __init__(self):
        # ONLY use Streamlit secrets in production
        api_key = None
        
        # Force use of Streamlit secrets (ignore .env completely)
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
                st.success("✅ Using API key from Streamlit secrets")
            else:
                st.error("""
                ❌ API key not found in Streamlit secrets!
                
                Please add your OpenAI API key:
                1. Go to your app dashboard at share.streamlit.io
                2. Click '⋮' → 'Settings' → 'Secrets'
                3. Add: OPENAI_API_KEY = "your-real-key-here"
                4. Save and refresh this page
                """)
                self.client = None
                return
        except Exception as e:
            st.error(f"Error accessing secrets: {str(e)}")
            self.client = None
            return
            
        # Validate the key
        if not api_key or "your_actual" in api_key or "your-real" in api_key:
            st.error("""
            ❌ Invalid API key detected!
            
            Please make sure you've added your REAL OpenAI API key to Streamlit Secrets.
            The key should start with 'sk-proj-' and not contain placeholder text.
            """)
            self.client = None
            return
            
        self.client = OpenAI(api_key=api_key)
        self.current_document = ""
        st.success("🔑 API key validated successfully!")
    
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
