import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize with credentials if available
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default credentials (useful for cloud environments)
            try:
                firebase_admin.initialize_app()
            except Exception:
                print("Warning: Firebase not initialized. Firestore will not work.")
                return None
    
    return firestore.client()

db = get_db()
