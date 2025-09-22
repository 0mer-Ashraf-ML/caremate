from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import users, clients, documents, template

app = FastAPI(title="NDIS Support Coordinator API")

# CORS for Streamlit frontend
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# API routes
app.include_router(users.router, prefix="/api/users")
app.include_router(clients.router, prefix="/api/clients") 
app.include_router(documents.router, prefix="/api/documents")
app.include_router(template.router, prefix="/api/template")