import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from schema import schema
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HireIntel Backend")

# Security configuration from environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_CORS_ORIGINS", "*").split(",")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Enable CORS for the browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://kpgchijndeoboichpekpmlkekkekfacd"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"Server starting on {APP_HOST}:{APP_PORT}...")
print(f"CORS Allowed Origins: {ALLOWED_ORIGINS}")

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "HireIntel API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
