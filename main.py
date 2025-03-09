from fastapi import FastAPI, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import videodb
from videodb import connect, SceneExtractionType, IndexType, SearchType
import os
import shutil
from utils import combine_with_opposite,  true_classification  # Assuming this exists

app = FastAPI()
origins = ["http://localhost:5173/realtime",
           "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configuration
OPENAI_API_KEY = ""
VIDEODB_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["VIDEODB_KEY"] = VIDEODB_KEY

# VideoDB connection
conn = connect(api_key=VIDEODB_KEY)
coll = conn.get_collection()

# Global variables
prompts = []
real_time_on = False
current_video = None  # Store the latest processed video

class PromptList(BaseModel):
    prompt: list

class ChatInput(BaseModel):
    chat: str
    mode: str

class VideoURL(BaseModel):
    url: str

RECEIVED_DIR = "server_received_vids"
os.makedirs(RECEIVED_DIR, exist_ok=True)
@app.post("/real_time")
async def real_time(file: UploadFile = File(...)):
    global current_video, real_time_on
    if file.content_type != "video/mp4":
        return {"error": "Only MP4 files are allowed"}

    file_path = os.path.join("server_received_vids", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print("printing",prompts)

   
    flagged = true_classification("server_received_vids/video_chunk.mp4", prompts, combine_with_opposite(prompts))
    print(flagged)
    # time.sleep(10)
    os.remove(file_path)
    
    real_time_on = True
    return {"message": "Real-time video chunk processed", "filename": file.filename}

    
@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    global current_video
    if file.content_type != "video/mp4":
        return {"error": "Only MP4 files are allowed"}
    
    file_path = os.path.join(".", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    current_video = coll.upload(file_path)
    stream = current_video.generate_stream()
    current_video.index_spoken_words()
    index_id = current_video.index_scenes(
        extraction_type=SceneExtractionType.time_based,
        extraction_config={"time": 2, "select_frames": ["first", "last"]},
        prompt="Describe the scene in detail",
    )
    current_video.get_scene_index(index_id)
    
    os.remove(file_path)
    return {"message": "Video uploaded successfully", "filename": file.filename}

@app.post("/upload_video_url")
async def upload_video_url(data: VideoURL):
    global current_video
    data = jsonable_encoder(data)
    current_video = coll.upload(url=data['url'])
    print("processing video")
    stream = current_video.generate_stream()
    current_video.index_spoken_words()
    index_id = current_video.index_scenes(
        extraction_type=SceneExtractionType.time_based,
        extraction_config={"time": 2, "select_frames": ["first", "last"]},
        prompt="Describe the scene in detail",
    )
    print("video is processed")
    # current_video.get_scene_index(index_id)
    return {"success": True}

@app.post("/chat")
async def chat(data: ChatInput):
    data = jsonable_encoder(data)
    chat = data['chat']
    mode = data['mode']
    print(mode)
    print(chat)
    if not current_video:
        return {"error": "No video uploaded yet"}
    
    if mode == "spoken":
        results = current_video.search(
            query=chat,
            index_type=IndexType.spoken_word,
            search_type=SearchType.semantic,
        )
    else:
        results = current_video.search(
            query=chat,
            index_type=IndexType.scene,
            search_type=SearchType.semantic,
            score_threshold=0.1,
            dynamic_score_percentage=100,
        )
    print(results)
    return {"stream": "https://stream.videodb.io/v3/published/manifests/ab2083e5-d2ea-4976-a85c-6bb4f4bb0647.m3u8", "player": "https://console.videodb.io/player?url=https://stream.videodb.io/v3/published/manifests/ab2083e5-d2ea-4976-a85c-6bb4f4bb0647.m3u8"}

@app.post("/camera")
async def camera(data):
    return {"data": data}

@app.post("/prompt")
async def prompt(data: PromptList):
    global prompts, real_time_on
    data = jsonable_encoder(data)
    prompts = data['prompt']
    real_time_on = True
    return {"success": "Prompt added successfully"}

