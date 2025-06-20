import os
import cv2
from ultralytics import YOLO  # type: ignore
from deep_sort_realtime.deepsort_tracker import DeepSort  # type: ignore

# Correct video path (ensure no extra spaces in filename)
video_path = "C:/Users/Public/Documents/Completed/project-potential/parking-lot-1 .mp4"

if not os.path.exists(video_path):
    print(f"❌ Error: Video file '{video_path}' does not exist.")
    exit()
else:
    print(f"✅ Video file '{video_path}' found.")

# Load YOLOv8 model
model = YOLO("yolov8s.pt")  # Change to yolov8m.pt for better accuracy

# Initialize Deep SORT tracker (n_init=1 confirms tracks faster)
tracker = DeepSort(max_age=30, n_init=1, max_cosine_distance=0.6)

# Open video stream
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ Error: Could not open video file at {video_path}")
    exit()

# (Optional) Save output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('tracked_output.mp4', fourcc, 30,
                      (int(cap.get(3)), int(cap.get(4))))

counted_ids = set()
total_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("✅ End of video reached.")
        break

    # Run YOLOv8 detection
    results = model(frame)[0]
    # Optional: visualize all detections as red boxes
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        class_name = model.names[int(class_id)]
        if score > 0.1:
           cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 1)
           cv2.putText(frame, class_name, (int(x1), int(y1) - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    detections = []

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        class_id = int(class_id)
        class_name = model.names[class_id]

        # Print filtered log messages
        if class_name == "car":
            print(f"✅ Car detected: class_id={class_id}, score={score}")
        elif score > 0.2:
            print(f"⛔ Ignored: {class_name} (class_id={class_id}, score={score})")

        # Only track cars above a low score threshold
        if class_name == "car" and score > 0.1:
            detections.append(([x1, y1, x2 - x1, y2 - y1], score, 'car'))

    print("Detections this frame:", detections)

    # Update Deep SORT tracker
    tracks = tracker.update_tracks(detections, frame=frame)

    print(f"Tracks this frame ({len(tracks)}): {[track.track_id for track in tracks]}")

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, r, b = track.to_ltrb()

        # Draw bounding box and label
        cv2.rectangle(frame, (int(l), int(t)), (int(r), int(b)), (0, 255, 0), 2)
        cv2.putText(frame, f'Car {track_id}', (int(l), int(t) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Count unique car IDs
        if track_id not in counted_ids:
            counted_ids.add(track_id)
            total_count += 1

    # Display total count
    cv2.putText(frame, f'Total Cars: {total_count}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show frame and write to file
    cv2.imshow("Car Detection and Tracking", frame)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("🛑 Quit key pressed. Exiting.")
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
