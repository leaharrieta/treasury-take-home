from fastapi import FastAPI

# FastAPI application
app = FastAPI()

# Return confirmation message
@app.get("/")
def home():
    return {"message": "API is running"}