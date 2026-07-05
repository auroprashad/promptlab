import sys
import os
from huggingface_hub import HfApi

try:
    # HfApi will load token from standard cache location (configured via hf auth login)
    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/promptlab-chat"
    print(f"AUTHENTICATED: Logged in as '{username}'. Target Space: '{repo_id}'")
    
    # Create Space repo if not already exists
    print("CREATING REPO: Initializing Hugging Face Space...")
    try:
        api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="gradio", private=False)
        print("SUCCESS: Space created successfully!")
    except Exception as e:
        # If the repository is already created, we just proceed with pushing files
        print(f"INFO: Repository creation info: {e}. Proceeding to upload files...")
            
    # Push folder contents
    print("UPLOADING: Pushing workspace files to Space...")
    
    # Resolve the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    api.upload_folder(
        folder_path=current_dir,
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["venv/*", ".git/*", "__pycache__/*", "*.pyc", "*.log", "deploy_hf.py"]
    )
    print(f"SUCCESS: Upload complete! Space url: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    print(f"ERROR: Deploy failed: {e}")
    sys.exit(1)
