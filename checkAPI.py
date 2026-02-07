import streamlit as st
from google import genai
import os

# 1. Setup your key (Replace with your actual key)
api_key = st.secrets["GEMINI_API_KEY"]
os.environ["GEMINI_API_KEY"] = api_key

def verify_gemini():
    try:
        # 2. Initialize the client
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        
        # 3. Test with a simple prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Hello! Are you working?"
        )
        
        print("✅ API Key Verified!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    verify_gemini()