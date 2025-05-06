from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', os.getenv('SUPABASE_KEY'))

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        'Missing required Supabase environment variables. '
        'Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file.'
    )

# Initialize Supabase client - Sử dụng Service Role Key để bỏ qua RLS
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)