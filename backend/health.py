# Health check endpoint
import uvicorn
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {
        "status": "healthy",
        "service": "chatbot-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
