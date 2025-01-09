import cv2
import mediapipe as mp
import pygame
import os
import time

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame for music playback
pygame.mixer.init()

# Scan the music folder
music_files = [os.path.join('music', f) for f in os.listdir('music') if f.endswith('.mp3')]
current_track = 0

def play_music(index):
    pygame.mixer.music.load(music_files[index])
    pygame.mixer.music.play()

# Function to detect if thumb is up
def is_thumb_up(hand_landmarks):
    return hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y

# Function to detect if hand is closed
def is_hand_closed(hand_landmarks):
    fingers = [hand_landmarks.landmark[i].y for i in [8, 12, 16, 20]]
    thumb = hand_landmarks.landmark[4].x
    closed_fingers = sum([1 for finger in fingers if finger > hand_landmarks.landmark[0].y])
    return closed_fingers == 4 and thumb < hand_landmarks.landmark[3].x

# Function to detect specific finger raised
def is_finger_raised(hand_landmarks, finger_index):
    return hand_landmarks.landmark[finger_index].y < hand_landmarks.landmark[finger_index - 2].y

# Variables for managing gestures and music control
gesture_timer = 0
gesture_cooldown = 30  # Number of frames to wait between detecting gestures

# Function to detect and interpret hand gestures
def detect_gesture(hand_landmarks):
    global current_track, gesture_timer

    if is_finger_raised(hand_landmarks, 8) and gesture_timer == 0:  # Index finger
        current_track = (current_track + 1) % len(music_files)
        play_music(current_track)
        gesture_timer = gesture_cooldown
    elif is_finger_raised(hand_landmarks, 20) and gesture_timer == 0:  # Little finger
        current_track = (current_track - 1) % len(music_files)
        play_music(current_track)
        gesture_timer = gesture_cooldown

    if is_thumb_up(hand_landmarks):
        pygame.mixer.music.unpause()
    elif is_hand_closed(hand_landmarks):
        pygame.mixer.music.pause()

# Start playing the first track
play_music(current_track)

# Initialize webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image_rgb)

    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            detect_gesture(hand_landmarks)

    # Handle gesture cooldown timer
    if gesture_timer > 0:
        gesture_timer -= 1

    # Display the image
    cv2.imshow('Hand Gesture Music Control', image)

    # Break the loop on 'q' key press
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
pygame.mixer.quit()
