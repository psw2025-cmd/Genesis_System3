import os
import sys
from google.cloud import secretmanager
import uvicorn

# 1. Force the working directory to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.insert(0, project_root)

def clone_cloud_to_local():
    project_id = "system3-openalgo-safe"
    
    # The ACTUAL names in your Google Cloud Secret Manager
    secret_mapping = {
        "dhan-client-id": "DHAN_CLIENT_ID",
        "dhan-pin": "DHAN_PIN",
        "dhan-totp-secret": "DHAN_TOTP_SECRET",
        "dhan-access-token": "DHAN_ACCESS_TOKEN"
    }
    
    # The client will automatically use the GOOGLE_APPLICATION_CREDENTIALS variable
    client = secretmanager.SecretManagerServiceClient()
    
    for secret_name, env_var_name in secret_mapping.items():
        try:
            path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": path})
            val = response.payload.data.decode("UTF-8").strip()
            
            # Set the UPPERCASE environment variable that the app expects
            os.environ[env_var_name] = val
            print(f"✅ Cloned {env_var_name} from Google Cloud")
        except Exception as e:
            print(f"⚠️ Could not clone {secret_name}: {e}")

if __name__ == "__main__":
    clone_cloud_to_local()
    print("Starting Local Uvicorn Server with Cloud Credentials...")
    
    # Start the UI (now running from the correct root directory)
    uvicorn.run("dashboard.backend.app:app", host="127.0.0.1", port=8000, reload=True)
