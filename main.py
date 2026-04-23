import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routes import router

app = FastAPI(
    title="Stock Intelligence API",
    description="Backend for the Stock News Analysis Platform",
    version="1.0.0",
)

# allow frontend dashboard to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(router)

if __name__ == "__main__":
    print("Starting FastAPI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
