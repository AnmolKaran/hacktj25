import cv2
import numpy as np

# Load video
input_video_path = "backend/HackTJ25RealTimeDemo.mp4"
output_video_path = "backend/output.mp4"

cap = cv2.VideoCapture(input_video_path)

# Get video properties
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Background subtractor for movement detection
fgbg = cv2.createBackgroundSubtractorMOG2()

# Variable to track previous height of detected person
previous_height = None
collapse_detected = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert frame to grayscale
    
    # Write the frame with bounding box only if collapse is detected
    out.write(frame)
    
    # Uncomment to preview the video while processing
    # cv2.imshow('Frame', frame)
    # if cv2.waitKey(30) & 0xFF == ord('q'):
    #     break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Processing complete. Saved as", output_video_path)
