import streamlit as st
from google import genai
from google.genai import types
import plotly.graph_objects as go
import json
import trafilatura

# --- 1. INITIAL CONFIG & STATE ---
st.set_page_config(layout="wide", page_title="Neutralise.AI", page_icon="🛡️")

if 'last_tab' not in st.session_state:
    st.session_state.last_tab = "📄 Paste Text"
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

# 2. Setup Client
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- 3. HELPER FUNCTIONS ---
def extract_from_url(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return None

# --- 4. 2026 SENSATIONAL UI (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #07070a 100%);
        background-attachment: fixed;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.status-card) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
    }
    .main-title {
        font-size: 60px !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        animation: glow 3s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(79, 172, 254, 0.2)); }
        to { filter: drop-shadow(0 0 20px rgba(255, 75, 75, 0.6)); }
    }
    .stButton>button {
        border-radius: 12px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .status-card { color: #e0e0e0; line-height: 1.6; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. HEADER ---
st.markdown('<h1 class="main-title">NEUTRALISE.AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#4facfe; font-family:monospace; letter-spacing: 2px;">NEURAL ENGINE ACTIVE // 2026_CORE</p>', unsafe_allow_html=True)

system_instruction = """
You are a professional neutral text editor specializing in linguistic de-biasing. 
Return strictly valid JSON:
1. "scores": {Political Leaning, Sensationalism, Subjectivity, Omission, Aggressive Tone} (0.0 to 1.0)
2. "neutral_text": Rewritten text to be neutral.
3. "justification": One-sentence explanation of bias.
"""

# --- 6. MAIN LAYOUT & TAB LOGIC ---
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### 📥 SOURCE FEED")
    active_tab = st.radio("INPUT MODE", ["📄 Paste Text", "🔗 Analysis via URL"], horizontal=True, label_visibility="collapsed")

    if active_tab != st.session_state.last_tab:
        st.session_state.manual_text = ""
        st.session_state.url_text = ""
        st.session_state.analyzed = False
        st.session_state.last_tab = active_tab
        st.rerun()

    user_input = ""
    if active_tab == "📄 Paste Text":
        user_input = st.text_area("Source Text:", height=300, key="manual_text")
    elif active_tab == "🔗 Analysis via URL":
        url_input = st.text_input("Article URL:", key="url_text")
        if url_input:
            with st.status("Scraping...", expanded=False) as s:
                extracted = extract_from_url(url_input)
                if extracted:
                    user_input = extracted
                    s.update(label="Ready!", state="complete")

    process_btn = st.button("EXECUTE DE-BIAS PROTOCOL")

# --- 7. ANALYSIS & RESULTS ---
if process_btn and user_input:
    st.session_state.analyzed = False 
    with st.spinner("Analyzing..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(system_instruction=system_instruction, response_mime_type="application/json")
            )
            data = json.loads(response.text)
            
            with col2:
                st.markdown("### 📄 RECONSTRUCTED TEXT")
                with st.expander("VIEW FULL NEUTRALIZED VERSION", expanded=False):
                    st.markdown(f'<div class="status-card" style="border: 1px solid #4facfe; padding: 15px; border-radius: 12px;">{data.get("neutral_text", "")}</div>', unsafe_allow_html=True)
                
                st.divider()
                st.markdown("### 🛰️ DIAGNOSTIC REPORT")
                
                categories = list(data['scores'].keys())
                bias_scores = list(data['scores'].values())
                neutral_scores = [round(1.0 - v, 2) for v in bias_scores]

                fig = go.Figure()
                fig.add_trace(go.Bar(y=categories, x=[-v for v in bias_scores], orientation='h', name='Bias', marker_color='#FF4B4B'))
                fig.add_trace(go.Bar(y=categories, x=neutral_scores, orientation='h', name='Neutrality', marker_color='#00f2fe'))

                fig.update_layout(
                    barmode='relative', height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickvals=[-1, -0.5, 0, 0.5, 1], ticktext=["100%", "50%", "0", "50%", "100%"]),
                    margin=dict(l=80, r=80, t=20, b=20), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{hash(user_input[:20])}")
                st.info(f"**AI FORENSIC INSIGHT:** {data.get('justification', 'Neutralized.')}")
            st.session_state.analyzed = True
        except Exception as e:
            st.error(f"Error: {e}")