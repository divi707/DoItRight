import cv2
import mediapipe as mp
import sys
import time
import tkinter as tk
from tkinter import filedialog
from types_of_exercise import TypeOfExercise
from mediapipe.python.solutions import drawing_utils as mp_drawing

def main(video_path=None):

    mp_pose = mp.solutions.pose


    if video_path is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #UI frame 
    cv2.namedWindow('Real-time Pose Classification', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Real-time Pose Classification', width, height)

    # Initialize Pose model
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        pose_start_time = None
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break


            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # pose landmarks
            results = pose.process(rgb_frame)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                #real-time classification 
                exercise_classifier = TypeOfExercise(landmarks)
                classified_exercise = exercise_classifier.classify_exercise()

                # Display the classified exercise label
                cv2.putText(frame, classified_exercise, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                # Draw landmarks/sticks
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Provide feedback on form for specific exercises
                if classified_exercise == 'Dead Hang':
                    left_arm_angle = exercise_classifier.angle_of_the_left_arm()
                    right_arm_angle = exercise_classifier.angle_of_the_right_arm()
                    if 160 <= left_arm_angle <= 180 and 160 <= right_arm_angle <= 180:
                        cv2.putText(frame, "Good form!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Straighten your arms!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif classified_exercise == 'Plank':
                    abdomen_angle = exercise_classifier.angle_of_the_abdomen()
                    if abdomen_angle > 150:
                        cv2.putText(frame, "Good form!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Straighten your back!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Check if the pose is being held
                if classified_exercise != 'Unknown Pose':
                    if pose_start_time is None:
                        pose_start_time = time.time()
                    else:
                        pose_duration = time.time() - pose_start_time
                        cv2.putText(frame, f'Pose Duration: {int(pose_duration)} seconds', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    pose_start_time = None

            # Display the frame with the classified exercise label
            cv2.imshow('Real-time Pose Classification', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release the VideoCapture object and close all windows
    cap.release()
    cv2.destroyAllWindows()

def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    if video_path:
        main(video_path)

def select_webcam():
    main()

# Create the main application window
root = tk.Tk()
root.title("Select Input Source")

# Create buttons for selecting webcam or video file
webcam_button = tk.Button(root, text="Webcam", command=select_webcam)
webcam_button.pack()

video_button = tk.Button(root, text="Select Video", command=select_video)
video_button.pack()

# Start the GUI application
root.mainloop()
