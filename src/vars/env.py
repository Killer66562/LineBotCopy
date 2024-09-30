from dotenv import load_dotenv

import os


load_dotenv()

access_token = os.getenv("LINE_ACCESS_TOKEN")
secret = os.getenv("LINE_SECRET")
base_api_url = os.getenv("BASE_API_URL").removesuffix("/")