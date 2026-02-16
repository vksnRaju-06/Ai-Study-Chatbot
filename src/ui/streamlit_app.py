"""
Streamlit UI for Study Assistant
Provides interactive interface for students
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.study_assistant import StudyAssistant
from src.patterns.singleton import config


# Page configuration
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .strategy-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        background-color: #e1f5ff;
        color: #0277bd;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    .hint-count {
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'assistant' not in st.session_state:
        st.session_state.assistant = StudyAssistant()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'ollama_status' not in st.session_state:
        st.session_state.ollama_status = None


def display_sidebar():
    """Display sidebar with info and controls"""
    with st.sidebar:
        st.markdown("# 🎓 Study Assistant")
        st.markdown("---")
        
        # OLLAMA Status
        st.subheader("🔌 Connection Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Check OLLAMA", use_container_width=True):
                st.session_state.ollama_status = st.session_state.assistant.check_ollama_status()
        
        with col2:
            if st.button("Check Supabase", use_container_width=True):
                st.session_state.supabase_status = st.session_state.assistant.check_supabase_status()
        
        if st.session_state.ollama_status:
            status = st.session_state.ollama_status
            if status['available']:
                st.success(f"✅ OLLAMA: {status['model']}")
            else:
                st.error("❌ OLLAMA not available")
        
        # Supabase status
        if hasattr(st.session_state, 'supabase_status'):
            status = st.session_state.supabase_status
            if status.get('available'):
                st.success(f"✅ Supabase Connected")
                if status.get('session_id'):
                    st.caption(f"Session: {status['session_id'][:8]}...")
            else:
                st.warning("⚠️ Supabase Disabled")
        
        st.markdown("---")
        
        # Session Stats
        st.subheader("📊 Session Statistics")
        stats = st.session_state.assistant.get_session_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", stats['total_questions'])
        with col2:
            st.metric("Hints Used", stats['hints_requested'])
        
        if stats['questions_by_type']:
            st.markdown("**Question Types:**")
            for q_type, count in stats['questions_by_type'].items():
                st.text(f"• {q_type}: {count}")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("💡 Request Hint", use_container_width=True):
            result = st.session_state.assistant.request_hint()
            st.session_state.messages.append({
                'role': 'assistant',
                'content': result['response'],
                'metadata': result['metadata']
            })
            st.rerun()
        
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.assistant.reset_session()
            st.session_state.messages = []
            st.success("Session reset!")
            st.rerun()
        
        st.markdown("---")
        
        # Learning Tips
        st.subheader("💡 Learning Tips")
        st.info("""
        **How to get the most out of this assistant:**
        
        1️⃣ Ask your question clearly
        
        2️⃣ Engage with the guiding questions
        
        3️⃣ Try to think before asking for hints
        
        4️⃣ Don't look for direct answers - focus on understanding!
        
        💡 **Hint System:** You can request up to 5 progressive hints. After the 5th hint, you'll receive the complete answer with full explanation.
        """)
        
        st.markdown("---")
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            This AI Study Assistant uses:
            - **Strategy Pattern** for learning approaches
            - **Factory Pattern** for response handling
            - **Observer Pattern** for progress tracking
            - **Chain of Responsibility** for question routing
            
            **Model:** OLLAMA with phi3:mini
            
            Built for educational purposes to promote active learning.
            """)


def display_chat_message(message):
    """Display a chat message with metadata"""
    role = message['role']
    content = message['content']
    
    with st.chat_message(role):
        st.markdown(content)
        
        # Display metadata for assistant messages
        if role == 'assistant' and 'metadata' in message:
            metadata = message['metadata']
            
            # Display strategy badge
            if 'strategy' in metadata:
                st.markdown(
                    f'<span class="strategy-badge">📚 {metadata["strategy"]}</span>',
                    unsafe_allow_html=True
                )
            
            # Display hint count if applicable
            if metadata.get('hint_count', 0) > 0:
                hint_count = metadata['hint_count']
                if hint_count > 5:
                    st.markdown(
                        f'<span class="hint-count">✅ Complete Answer (after 5 hints)</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<span class="hint-count">💡 Hint {hint_count}/5</span>',
                        unsafe_allow_html=True
                )


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎓 AI Study Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #666;">Your learning companion - I guide, you discover!</p>',
        unsafe_allow_html=True
    )
    
    # Display sidebar
    display_sidebar()
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-box">
            <h3>👋 Welcome to Your AI Study Assistant!</h3>
            <p>I'm here to help you <strong>learn</strong>, not just get answers. I will:</p>
            <ul>
                <li>Ask guiding questions to help you think critically</li>
                <li>Provide hints when you're stuck</li>
                <li>Explain concepts without solving your homework</li>
                <li>Help you develop problem-solving skills</li>
            </ul>
            <p><strong>Ask me anything you're learning about!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask your question here..."):
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt
        })
        
        # Display user message
        with st.chat_message('user'):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message('assistant'):
            with st.spinner('Thinking... 🤔'):
                result = st.session_state.assistant.process_question(prompt)
                
                response = result['response']
                metadata = result['metadata']
                
                st.markdown(response)
                
                # Display metadata
                if 'strategy' in metadata:
                    st.markdown(
                        f'<span class="strategy-badge">📚 {metadata["strategy"]}</span>',
                        unsafe_allow_html=True
                    )
                
                if metadata.get('hint_count', 0) > 0:
                    st.markdown(
                        f'<span class="hint-count">💡 Hint {metadata["hint_count"]}/3</span>',
                        unsafe_allow_html=True
                    )
        
        # Add assistant message to history
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response,
            'metadata': metadata
        })
        
        # Rerun to update sidebar stats
        st.rerun()


if __name__ == "__main__":
    main()
