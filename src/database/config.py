import streamlit as st

# create_client: Creates a connection between your Python application and Supabase.

# Client: A type hint that indicates the Supabase client object.


from supabase import create_client, Client
supabase : Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
    
)