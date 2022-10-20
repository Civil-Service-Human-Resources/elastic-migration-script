import os
from dotenv import load_dotenv

load_dotenv()

existing_elastic_repo_endpoint=os.getenv("EXISTING_ELASTIC_REPO_ENDPOINT")
existing_elastic_repo_username=os.getenv("EXISTING_ELASTIC_REPO_USERNAME")
existing_elastic_repo_password=os.getenv("EXISTING_ELASTIC_REPO_PASSWORD")
new_elastic_repo_endpoint=os.getenv("NEW_ELASTIC_REPO_ENDPOINT")
new_elastic_repo_username=os.getenv("NEW_ELASTIC_REPO_USERNAME")
new_elastic_repo_password=os.getenv("NEW_ELASTIC_REPO_PASSWORD")