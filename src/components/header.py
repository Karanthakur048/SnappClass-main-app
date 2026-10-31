import streamlit as st

def header_home():
    
        #snapchat logo  
    logo_url = "https://i.ibb.co/NdFhKB8y/Chat-GPT-Image-Sep-24-2026-11-03-07-PM.png"
    
     
    st.markdown(f""" 
        <div style = "display:flex;flex-direction:column;align-items:center;justify-content:content:center;margin-top:30px;margin-bottom:30px">           
        <img src = '{logo_url}' style = 'height : 100px';/>
        <h1 style = 'text-align:center; color:#E0E3FF'> SNAP<br/>CLASS</h1>        
        </div>       
                """,unsafe_allow_html = True)
    
    
def header_dashboard():
    
    #For Teache Screen
          
    logo_url = "https://i.ibb.co/NdFhKB8y/Chat-GPT-Image-Sep-24-2026-11-03-07-PM.png"
    
     
    st.markdown(f""" 
        <div style = "display:flex;align-items:cente;justify-content:content:center;margin-top:30px;gap:10px">           
        <img src = '{logo_url}' style = 'height : 90px';/>
        <h1 class = "Teachersnap" style = 'text-align:left; color:#5865F2'> SNAP<br/>CLASS</h1>        
        </div>       
                """,unsafe_allow_html = True)