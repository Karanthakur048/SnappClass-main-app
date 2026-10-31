import streamlit as st
def style_background_home():
    st.markdown("""
        <style>
                .stApp { 
                    background : #5865F2 !important;
                }
                
                .stApp div[data-testid = "stColumn"]{
                    background-color: #E0E3FF !important;
                    border-radius: 5rem !important;
                } 
                
                [data-testid="stImage"] {
                 padding-top: 20px;
                 padding-bottom: 10px;
                 padding-left: 60px;
                 padding-right: 30px;
                 }   
                 
                 
                 
                div.stButton>button{
                    
                    margin-left:54px!important;
                    margin-bottom:2px!important;
                    width:200px;
                  
                }    
        
        
             
                
                
        </style>
                
                """ 
                ,unsafe_allow_html = True)
                
               
          
          
def style_background_dashboard():
    st.markdown("""
        <style>
                .stApp {
                    background : #E0E3FF !important;
                }
        </style>
                
                """ 
                ,unsafe_allow_html = True)
                        
          
          
          
          
          
          
          
          
               
def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979..2050&display=swap');
        
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&family=Outfit:wght@100..900&display=swap');
        
        
        
        #MainMenu, footer, header {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.5rem !important;
        }
        
        
        .Teachersnap{
                    
           font-size:1.8rem !important;
            
                  
                    
        }
        
        .Teacher{
            white-space:nowrspace;
            margin-top: -5px !important;
            margin-bottom: 0 !important;
            margin-right: 330px !important;

        }
        
        
        
        
        
        h1{
                    
            font-family: 'Climate Crisis',sans-serif !important;
            font-size:2.5rem ! important;
            line-height:1!important;
            margin-bottom: 0rem !important;
            
            
                  
                    
        }
        
        
        
        


        h2{
            
            font-family: 'Climate Crisis',sans-serif !important;
            font-size:1.9rem !important;
            text-align: center !important;
            line-height:0.8!important;
            margin-bottom: 0rem !important;
            margin-top:10px !important;
            
            color:black!important;
            padding:10px;
            
            
        }
        
         h3,p,h4 {
            font-family:"Outfit", sans_serif;
         }
        
            button[kind = "secondary"] {
            border-radius: 1.5rem !important;
            background: #EB459E ! important;
            # color: white ;
            padding: 10px 20px !important;
            text-align:center !important;
            border:none !important;
            transition: transform 0.25s ease-in-out !important;
            
        }
        
            button{
            border-radius: 1.5rem !important;
            background: #5865F2 !important;
            color: white;
            padding: 10px 20px !important;
            border:none !important;
            transition: transform 0.25s ease-in-out !important;
            outline: none !important;
            box-shadow: none !important;
            
        }
    
        
            button[kind = "tertiary"] {
            border-radius: 1.5rem !important;
            background: #EB459E !important;
            color: white !important;
            padding: 10px 20px !important;
            border:none !important;
            transition: transform 0.25s ease-in-out !important;
            
        }
        
    button:hover{
        transform: scale(1.05)
        
    }    
        
        
        
        
     
        </style>
    """, unsafe_allow_html=True)