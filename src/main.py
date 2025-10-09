# src/main.py
# Frontend Interface for Hippocrates AI - Built with Streamlit

import streamlit as st
import json
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the RAG chain from our backend
from src.rag_chain import setup_rag_chain, get_response

# Set page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="Hippocrates AI",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS for professional styling with better visibility
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .disclaimer {
        background-color: #FFE5E5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .diagnosis-box {
        background-color: #F0F7FF;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 15px 0;
    }
    .red-flag {
        background-color: #FFE5E5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        margin: 10px 0;
        font-weight: bold;
        border: 2px solid #FF0000;
    }
    .next-steps {
        background-color: #E5FFE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00AA00;
        margin: 10px 0;
        font-weight: bold;
        border: 2px solid #00AA00;
    }
    .confidence-high {
        color: #00AA00;
        font-weight: bold;
    }
    .confidence-medium {
        color: #FFA500;
        font-weight: bold;
    }
    .confidence-low {
        color: #FF0000;
        font-weight: bold;
    }
    .section-header {
        background-color: #2E86AB;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 15px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the RAG chain in session state to avoid reloading on every interaction
if 'rag_chain' not in st.session_state:
    try:
        with st.spinner("🩺 Initializing Hippocrates AI... This may take a few moments."):
            st.session_state.rag_chain = setup_rag_chain()
        st.success("Hippocrates AI initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize AI: {e}")
        st.stop()

# Initialize chat history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a professional header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/color/96/medical-heart.png", width=80)
with col2:
    st.markdown("<h1 class='main-header'>Hippocrates AI</h1>", unsafe_allow_html=True)

# Display disclaimer
st.markdown("""
<div class='disclaimer'>
    <strong>⚠️ DISCLAIMER:</strong> This is a proof-of-concept for AI-assisted clinical reasoning. 
    It is NOT for medical use. Always consult a qualified healthcare professional for medical advice.
</div>
""", unsafe_allow_html=True)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for user messages
if prompt := st.chat_input("Describe the patient's symptoms or ask a question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🩺 Analyzing symptoms...")
        
        try:
            # Get response from the RAG chain
            response = get_response(st.session_state.rag_chain, prompt)
            ai_response = response['result']
            
            # Try to parse JSON response if available
            try:
                # Extract JSON from the response if it exists
                if "{" in ai_response and "}" in ai_response:
                    json_str = ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
                    parsed_response = json.loads(json_str)
                    
                    # Clear the thinking message
                    message_placeholder.empty()
                    
                    # Display structured response with better visibility
                    
                    # 1. DIFFERENTIAL DIAGNOSIS SECTION
                    st.markdown("<div class='section-header'>📋 DIFFERENTIAL DIAGNOSIS</div>", unsafe_allow_html=True)
                    
                    for diagnosis in parsed_response.get("differential_diagnosis", []):
                        # Color code based on confidence
                        confidence_color = {
                            "High": "🟢",
                            "Medium": "🟡", 
                            "Low": "🔴"
                        }.get(diagnosis['confidence'], "⚪")
                        
                        # Create a visually distinct box for each diagnosis
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{diagnosis['condition']}**")
                                st.markdown(f"*Evidence:* {diagnosis['evidence']}")
                            with col2:
                                confidence_class = f"confidence-{diagnosis['confidence'].lower()}"
                                st.markdown(f"<div class='{confidence_class}'>{confidence_color} {diagnosis['confidence']} Confidence</div>", unsafe_allow_html=True)
                            st.divider()
                    
                    # 2. RECOMMENDED NEXT STEPS SECTION - ALWAYS VISIBLE AND PROMINENT
                    if parsed_response.get("next_steps"):
                        st.markdown("<div class='section-header'>🎯 RECOMMENDED NEXT STEPS</div>", unsafe_allow_html=True)
                        
                        for i, step in enumerate(parsed_response["next_steps"], 1):
                            st.markdown(f"""
                            <div class='next-steps'>
                                ✅ <strong>Step {i}:</strong> {step}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 3. RED FLAGS SECTION - ALWAYS VISIBLE AND HIGHLY PROMINENT
                    if parsed_response.get("red_flags"):
                        st.markdown("<div class='section-header'>⚠️ CRITICAL RED FLAGS</div>", unsafe_allow_html=True)
                        
                        for i, flag in enumerate(parsed_response["red_flags"], 1):
                            st.markdown(f"""
                            <div class='red-flag'>
                                🚨 <strong>Red Flag {i}:</strong> {flag}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 4. FINAL DISCLAIMER
                    st.markdown("---")
                    st.info("""
                    💡 **Important Note:** This AI assistant is for educational and demonstration purposes only. 
                    It is not a substitute for professional medical advice, diagnosis, or treatment. 
                    Always consult with a qualified healthcare provider for medical decisions.
                    """)
                    
                    # Add the JSON response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    # If no JSON found, display the raw response
                    message_placeholder.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except json.JSONDecodeError:
                # If JSON parsing fails, display the raw response
                message_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        except Exception as e:
            message_placeholder.error(f"Error: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})

# Add a sidebar with information and controls
with st.sidebar:
    st.markdown("## About Hippocrates AI")
    st.markdown("""
    This is a proof-of-concept AI system designed to demonstrate clinical reasoning capabilities for upper respiratory infections.
    
    **Current Knowledge Base:**
    - Common Cold
    - Influenza (Flu)
    - Strep Pharyngitis
    - COVID-19
    - Allergic Rhinitis
    
    **How to use:**
    1. Describe the patient's symptoms.
    2. The AI will provide a differential diagnosis.
    3. Review the recommended next steps and red flags.
    """)
    
    st.markdown("---")
    
    # Button to clear chat history
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Technical Information")
    st.markdown("""
    - **AI Model:** Rule-based Medical Diagnosis System
    - **Knowledge Base:** 5 medical conditions
    - **Vector Database:** ChromaDB
    - **Framework:** LangChain + Streamlit
    """)