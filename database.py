import os

from supabase import create_client
from dotenv import load_dotenv


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY are missing from .env"
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def insert_wcr_data(data):

    response = supabase.table(
        "WCR_Structured_DB"
    ).insert(data).execute()

    return response


def get_all_wcr_data():

    response = supabase.table(
        "WCR_Structured_DB"
    ).select("*").order(
        "created_at",
        desc=True
    ).execute()

    return response.data