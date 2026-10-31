import streamlit as st

from src.screen.student_screen import student_screen
from src.screen.home_screen import home_screen
from src.screen.teacher_screen import teacher_screen
def main():
    #its a temporary storage/memory that remembers values even when the app returns
    st.set_page_config(
        page_title = 'SnapClass - Making Attendance faster using AI',
        page_icon = "https://i.ibb.co/NdFhKB8y/Chat-GPT-Image-Sep-24-2026-11-03-07-PM.png"
    )
    
    if "login_type" not in st.session_state:
        st.session_state['login_type'] = None
    
    match st.session_state["login_type"]:
        case 'teacher':
            teacher_screen()
        case "student":
            student_screen()  
        case None:
            home_screen()       
main()