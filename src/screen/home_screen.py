import streamlit as  st
from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_home
def home_screen():
    header_home()
    style_base_layout()
    style_background_home()
    
    
   
    col1,col2 = st.columns(2, gap ="large")
    
    with col1:
        st.header("I'm Student")
        st.image("https://i.ibb.co/SXWvhBKL/student-illustration-1385x1136.png",width = 200 )
        if st.button("Student portal",type = "tertiary",icon = ":material/arrow_outward:"):
            
            st.session_state['login_type'] ='student'    
            st.rerun()
                      
    
    
    
    with col2:
        st.header("I'm Teacher")
        st.image("https://i.ibb.co/x82r87RG/Chat-GPT-Image-Sep-25-2026-12-10-15-PM.png",width = 200)
     
        
        if st.button("Teacehr Portal",type = "secondary",icon = ":material/arrow_outward:"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
