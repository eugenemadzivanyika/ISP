import cv2
import requests

cap = cv2.VideoCapture("live-parking-lot.mp4")

API_URL = "http://localhost:8000/api/vehicles/log/"

def log_vehicle(action):  # 'entry' or 'exit'
    try:
        requests.post(API_URL, json={"action": action})
    except Exception as e:
        print("Failed to log vehicle:", e)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Couldn't open the video file.")
    exit()

# Initialize background subtractors for entry and exit
object_detector_entry = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=55, detectShadows=False)
object_detector_exit = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=55, detectShadows=False)

# Initialize car counts
car_count_entry = 0
car_count_exit = 0

# Detection flags for entry and exit
detected_entry = False
detected_exit = False

# Open a log file for off-screen display
log_file = open("car_count_log.txt", "w")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Video ended.")
        break

    height, width, _ = frame.shape

    # Define entry and exit ROIs
    roi_entry = frame[400:500, 0:110]
    roi_exit = frame[100:200, 0:125]

    # ===== ENTRY DETECTION =====
    mask_entry = object_detector_entry.apply(roi_entry)
    _, mask_entry = cv2.threshold(mask_entry, 254, 255, cv2.THRESH_BINARY)

    contours_entry, _ = cv2.findContours(mask_entry, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detected_in_entry = False
    for cnt in contours_entry:
        if cv2.contourArea(cnt) > 300:  # Threshold for contour area
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi_entry, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(roi_entry, "Car Entering", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            detected_in_entry = True

    if detected_in_entry and not detected_entry:
        car_count_entry += 1
        print(f"🚗 Car Entered! Total: {car_count_entry}")
        # log_file.write(f"🚗 Car Entered! Total: {car_count_entry}\n")  # Log to file
        log_vehicle("entry")  # or "exit"
    detected_entry = detected_in_entry

    # ===== EXIT DETECTION =====
    mask_exit = object_detector_exit.apply(roi_exit)
    _, mask_exit = cv2.threshold(mask_exit, 254, 255, cv2.THRESH_BINARY)

    contours_exit, _ = cv2.findContours(mask_exit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detected_in_exit = False
    for cnt in contours_exit:
        if cv2.contourArea(cnt) > 300:  # Threshold for contour area
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi_exit, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(roi_exit, "Car Exiting", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            detected_in_exit = True

    if detected_in_exit and not detected_exit:
        car_count_exit += 1
        print(f"⬅️ Car Exited! Total: {car_count_exit}")
        # log_file.write(f"⬅️ Car Exited! Total: {car_count_exit}\n")  # Log to file
        log_vehicle("exit")  # or "exit"
    detected_exit = detected_in_exit

    # ===== DISPLAY COUNT ON MAIN FRAME =====
    cv2.putText(frame, f"Cars Entered: {car_count_entry}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.putText(frame, f"Cars Exited: {car_count_exit}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    # Show main video feed
    cv2.imshow("Live Feed", frame)

    # Show individual ROIs for debugging (entry and exit regions)
    # cv2.imshow("Entry ROI", roi_entry)
    # cv2.imshow("Exit ROI", roi_exit)

    # Wait for a key press, with slow playback
    key = cv2.waitKey(150)
    if key == 27:  # ESC key
        break

# Close the log file and release video capture
log_file.close()
cap.release()
cv2.destroyAllWindows()
