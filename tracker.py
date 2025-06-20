import os
from pydoc import classname

video_path = "C:/Users/Public/Documents/Completed/project-potential/parking-lot-1 .mp4"
if not os.path.exists(video_path):
    print(f"Error: Video file '{video_path}' does not exist.")
else:
    print(f"Video file '{video_path}' found.")
    
import cv2
from ultralytics import YOLO  # type: ignore
from deep_sort_realtime.deepsort_tracker import DeepSort  # type: ignore

# Load YOLOv8 model (pre-trained on COCO, which includes 'car' class)
model = YOLO("yolov8n.pt")  # or yolov8s.pt for better accuracy

# Initialize Deep SORT tracker
tracker = DeepSort(max_age=30)

# Open video stream
cap = cv2.VideoCapture("parking-lot-1 .mp4")  # Replace with 0 for webcam

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

counted_ids = set()
total_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab a frame from the video.")
        break
    # Run YOLOv8 detection
    results = model(frame)[0]
    detections = []

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        class_id = int(class_id)
        class_name = model.names[class_id]
    
    # Print class name and class_id to see what is being detected
    print(f"Detected class_id: {class_id}, class_name: {model.names[class_id]}, score: {score}")
    
    # 🔍 Filtered log messages (place this right here)
    if class_name == "car":
        print(f"✅ Car detected: class_id={class_id}, score={score}")
    elif score > 0.2:
        print(f"⛔ Ignored: {class_name} (class_id={class_id}, score={score})")
    if model.names[class_id] == "car" and score > 0.2:
        detections.append(([x1, y1, x2 - x1, y2 - y1], score, 'car'))
        

    # ✅ Debug: Print detections before tracking
    print("Detections this frame:", detections)

    

    # Update Deep SORT tracker
    tracks = tracker.update_tracks(detections, frame=frame)

    # ✅ Debug: Print track info
    print(f"Tracks this frame ({len(tracks)}):")
    for track in tracks:
        print(f"  Track ID: {track.track_id}, Confirmed: {track.is_confirmed()}, Box: {track.to_ltrb()}")

    
    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = track.to_ltrb()
        cv2.rectangle(frame, (int(l), int(t)), (int(w), int(h)), (0, 255, 0), 2)
        cv2.putText(frame, f'Car {track_id}', (int(l), int(t) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Count unique car IDs
        if track_id not in counted_ids:
            counted_ids.add(track_id)
            total_count += 1

    # Display count
    cv2.putText(frame, f'Total Cars: {total_count}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Car Detection and Tracking", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()




