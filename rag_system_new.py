import streamlit as st
from openai import OpenAI

class SimpleRAG:
    def __init__(self):
        st.write("🔥 FRESH DEPLOYMENT - API Key Check Starting...")
        
        if 'OPENAI_API_KEY' not in st.secrets:
            st.error("❌ CRITICAL: OPENAI_API_KEY not found in st.secrets")
            st.info("Please add your key to Streamlit Secrets dashboard")
            self.client = None
            return
            
        api_key = st.secrets['OPENAI_API_KEY']
        st.write(f"📋 Key preview: {api_key[:25]}...")
        
        if any(x in api_key for x in ["your_actual", "your-real", "placeholder"]):
            st.error("🚫 INVALID: Key contains placeholder text")
            self.client = None
            return
            
        if len(api_key) < 50:
            st.error("📏 INVALID: Key too short")
            self.client = None
            return
            
        try:
            st.write("🔐 Testing API key...")
            self.client = OpenAI(api_key=api_key)
            models = self.client.models.list()
            st.success("🎉 SUCCESS: API Key is valid and working!")
            st.info(f"✅ Connected to OpenAI with {len(list(models))} models available")
        except Exception as e:
            st.error(f"💥 API Key Test Failed: {str(e)}")
            self.client = None
            return
            
        self.current_document = ""
        st.balloons()
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
            st.success("📄 Document processed successfully!")
    
    def query(self, question):
        if not self.client:
            return "System not ready - check API key configuration above."
        if not self.current_document:
            return "Please upload a document first."
            
        try:
            with st.spinner("🧠 Analyzing your document..."):
                prompt = f"""Based ONLY on the following context:

{self.current_document}

Question: {question}

Answer based only on the context above:"""
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return f"**Answer:** {response.choices[0].message.content}"
        except Exception as e:
            return f"❌ Error during AI processing: {str(e)}"
