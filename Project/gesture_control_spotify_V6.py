import cv2
import pyautogui
from HandTrackingModule import handDetector
import time
import os

# Start Spotify (only works if Spotify is installed and the system supports the "start" command)
os.system("start spotify:")

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Initialize hand detector
detector = handDetector(detectionCon=0.6)

# Set camera resolution
wCam, hCam = 640, 480
cap.set(3, wCam)
cap.set(4, hCam)

# Variables
pTime = 0

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to grab frame.")
        break

    # Find hands and landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Thumb tip and index tip positions
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip

        # Calculate distance between thumb and index finger
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Gesture: Play/Pause (Pinch Gesture)
        if length < 30:
            pyautogui.press("playpause")
            time.sleep(0.5)  # Adjust sleep time for faster response

        # Gesture: Next Track (Swipe Right)
        if lmList[4][1] > 500:  # Thumb on the right edge of the screen
            pyautogui.press("nexttrack")
            time.sleep(0.5)

        # Gesture: Previous Track (Swipe Left)
        if lmList[4][1] < 100:  # Thumb on the left edge of the screen
            pyautogui.press("prevtrack")
            time.sleep(0.5)

        # Gesture: Volume Up/Down (Based on Thumb and Index Distance)
        if length > 150:  # Spread fingers apart
            pyautogui.press("volumeup")
        elif length < 50:  # Fingers close together
            pyautogui.press("volumedown")

    # Display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    # Show the image
    cv2.imshow("Gesture Control", img)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
