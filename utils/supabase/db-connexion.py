import os
from supabase import create_client, Client


url: str = os.environ.get("https://jzpkojunkzsjijwemqvi.supabase.co")
key: str = os.environ.get("sb_publishable_paDQ1yWHah68_2BRML7HgA_oICCplk3")
supabase: Client = create_client(url, key)