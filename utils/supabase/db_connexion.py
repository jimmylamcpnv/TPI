import streamlit as st
from supabase import create_client, Client

# retrieve Supabase credentials from Streamlit secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# initialize the Supabase client
supabase: Client = create_client(url, key)