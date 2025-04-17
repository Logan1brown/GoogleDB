from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase admin client with service role key
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')  # Using service key to create user
)

# Test user credentials
TEST_EMAIL = "test@googledb-test.com"
TEST_PASSWORD = "TestUser123!"  # Strong password meeting requirements

try:
    # Create new user
    user = supabase.auth.admin.create_user({
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "email_confirm": True  # Auto-confirm email
    })
    
    print(f"""
✅ Test user created successfully!

Test User Credentials:
Email: {TEST_EMAIL}
Password: {TEST_PASSWORD}

Please update these credentials in test_policies.py
""")

except Exception as e:
    print(f"❌ Failed to create test user: {str(e)}")
