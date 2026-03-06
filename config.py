import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_BASE_URL=os.getenv("ADMIN_BASE_URL")
ADMIN_INTERNAL_KEY=os.getenv("ADMIN_INTERNAL_KEY")