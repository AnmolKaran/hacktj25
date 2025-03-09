from fastapi import FastAPI, File, UploadFile
from llama_index import VideoDB
import shutil
from pathlib import Path

app = FastAPI()

# Initialize VideoDB or other necessary classes
video_db = VideoDB()

# Endpoint for uploading video
@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Save the video to a temporary location
        temp_video_path = Path(f"./temp/{file.filename}")
        with temp_video_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Index the video with VideoDB
        video_db.index_video(str(temp_video_path))

        return {"message": f"Video {file.filename} uploaded and indexed successfully."}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to query video
@app.get("/query_video/{query}")
async def query_video(query: str):
    try:
        # Perform a video query using VideoDB
        results = video_db.query(query)
        return {"query": query, "results": results}
    except Exception as e:
        return {"error": str(e)}
