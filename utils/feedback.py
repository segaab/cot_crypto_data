import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components
import time
import requests
from streamlit_lottie import st_lottie
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Initialize Firebase (will only initialize once)
def init_firebase():
    """Initialize Firebase if not already initialized"""
    if not firebase_admin._apps:
        # Use service account from secrets
        cred = credentials.Certificate(st.secrets["firebase_service_account"])
        firebase_admin.initialize_app(cred)
    return firestore.client()

def save_feedback(email, feedback):
    """Save feedback to Firestore"""
    try:
        # Get Firestore client
        db = init_firebase()
        
        # Add timestamp
        timestamp = datetime.now()
        
        # Create feedback document
        feedback_data = {
            'feedback': feedback.strip(),
            'email': email.strip() if email else '',
            'timestamp': timestamp,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Add to 'feedback' collection
        db.collection('feedback').add(feedback_data)
        return True
        
    except Exception as e:
        st.error(f"Failed to save feedback: {str(e)}")
        return False

def load_lottie_url(url: str):
    """Load Lottie animation from URL"""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show_feedback_form():
    """Show feedback form"""
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False
        
    if 'show_thank_you' not in st.session_state:
        st.session_state.show_thank_you = False
    
    # Show thank you message if needed
    if st.session_state.show_thank_you:
        st.toast("Thank you for your feedback!", icon="✨")
        st.session_state.show_thank_you = False
        st.session_state.feedback_submitted = True
        st.rerun()
    
    # Show feedback form if not yet submitted
    with st.form("feedback_form", clear_on_submit=True):
        st.write("### Share Your Feedback")
        
        feedback = st.text_area(
            "Your Feedback",
            placeholder="Share your thoughts...",
            key="feedback_text",
            max_chars=1000
        )
        
        email = st.text_input(
            "Email (optional)",
            placeholder="your@email.com",
            key="feedback_email"
        )
        
        submit = st.form_submit_button("Submit")
        
        if submit:
            if email and '@' not in email:
                st.toast("Please enter a valid email address", icon="⚠️")
                return
            
            if feedback.strip():
                # Show sending notification immediately
                st.toast("Sending your feedback...", icon="📤")
                
                if save_feedback(email, feedback):
                    st.session_state.show_thank_you = True
                    st.rerun()
            else:
                st.toast("Please enter your feedback before submitting.", icon="⚠️")
                return 