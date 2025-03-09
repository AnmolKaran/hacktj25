import cv2
import time
import os
import requests
from datetime import datetime

SAVE_DIR = "video_chunks"
os.makedirs(SAVE_DIR, exist_ok=True)

SERVER_URL = "http://localhost:8000/real_time/"

def record_and_upload_chunks():
    cap = cv2.VideoCapture(0)  # 0 is usually the default webcam 
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30  
    chunk_duration = 30  
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_chunk.mp4"
            file_path = os.path.join(SAVE_DIR, filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(file_path, fourcc, fps, (frame_width, frame_height))
            
            start_time = time.time()
            
            print(f"Recording {filename}...")
            while time.time() - start_time < chunk_duration:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Can't receive frame")
                    break
                    
                out.write(frame)
                
                cv2.imshow('Webcam Preview', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            out.release()
            print(f"Saved {filename}")
            
            print(f"Sending {filename} to server...")
            try:
                with open(file_path, 'rb') as video_file:
                    files = {'file': (filename, video_file, 'video/mp4')}
                    response = requests.post(SERVER_URL, files=files)
                
                if response.status_code == 200:
                    print("Upload successful:", response.json())
                else:
                    print(f"Upload failed: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Error uploading file: {e}")
            
            try:
                os.remove(file_path)
                print(f"Deleted {file_path}")
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")

            elapsed = time.time() - start_time
            if elapsed < chunk_duration:
                time.sleep(chunk_duration - elapsed)
            
    except KeyboardInterrupt:
        print("Recording stopped by user")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    record_and_upload_chunks()