import os
from dotenv import load_dotenv

load_dotenv()

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("SESSION_SECRET:", os.getenv("SESSION_SECRET"))
print("UPLOAD_FOLDER:", os.getenv("UPLOAD_FOLDER"))
