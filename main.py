import cv2
import tkinter as tk
from tkinter import messagebox, filedialog
from utils import *
import mediapipe as mp
from body_part_angle import BodyPartAngle
from types_of_exercise import TypeOfExercise
from mediapipe.python.solutions import drawing_utils as mp_drawing

def select_exercise(exercise):
    global selected_exercise, video_source
    selected_exercise = exercise
    video_source = var.get()
    root.destroy()  # Close the GUI window
    display_video()

def select_video_file():
    global video_path
    video_path = filedialog.askopenfilename()
    print("Selected video file:", video_path)

def display_video():
    # Create the main application window for video display
    cv2.namedWindow("Video")

    if video_source == "Webcam":
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_path)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        counter = 0
        status = True
        window_open = True
        while window_open:
            try:
                ret, frame = cap.read()
                frame = cv2.resize(frame, (800, 480), interpolation=cv2.INTER_AREA)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                results = pose.process(frame)
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks is not None:
                    try:
                        landmarks = results.pose_landmarks.landmark
                        angles = {
                            "Left Arm Angle": BodyPartAngle(landmarks).angle_of_the_left_arm(),
                            "Right Arm Angle": BodyPartAngle(landmarks).angle_of_the_right_arm(),
                            "Left Leg Angle": BodyPartAngle(landmarks).angle_of_the_left_leg(),
                            "Right Leg Angle": BodyPartAngle(landmarks).angle_of_the_right_leg(),
                            "Neck Angle": BodyPartAngle(landmarks).angle_of_the_neck(),
                            "Abdomen Angle": BodyPartAngle(landmarks).angle_of_the_abdomen(),
                        }
                        
                        abdomen_angle = angles.get("Abdomen Angle", None)
                        if abdomen_angle is not None:
                            if abdomen_angle < 170 or abdomen_angle > 180:
                                cv2.putText(frame, "Straighten back", (frame.shape[1] - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            elif selected_exercise == "push-up":
                                cv2.putText(frame, "correct form", (frame.shape[1] - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        counter, status = TypeOfExercise(landmarks).calculate_exercise(selected_exercise, counter, status)
                        
                    except Exception as e:
                        print("Error:", e)
                        angles = {}

                else:
                    print("No pose landmarks detected")
                    angles = {}

                score_table(selected_exercise, counter, status)

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0) if status else (255, 0, 0),
                                            thickness=2,
                                            circle_radius=2),
                    mp_drawing.DrawingSpec(color=(174, 139, 45),
                                            thickness=2,
                                            circle_radius=2),
                )

                y = 30
                for angle_name, angle_value in angles.items():
                    cv2.putText(frame, f"{angle_name}: {angle_value:.2f} degrees", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                    y += 30

                cv2.imshow('Video', frame)
                key = cv2.waitKey(10)
                if key & 0xFF == ord('q'):
                    print("Counter:", counter)
                    window_open = False
            except Exception as e:
                print("Error:", e)
                window_open = False

    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Select Exercise")

exercises = ["push-up", "pull-up", "squat"]

label = tk.Label(root, text="Select Exercise:")
label.grid(row=0, column=0, padx=10, pady=5)

for i, exercise in enumerate(exercises):
    btn = tk.Button(root, text=exercise, command=lambda e=exercise: select_exercise(e), width=15, height=2)
    btn.grid(row=i+1, column=0, padx=10, pady=5)

label_source = tk.Label(root, text="Select Video Source:")
label_source.grid(row=len(exercises)+1, column=0, padx=10, pady=5)

var = tk.StringVar(root)
var.set("Webcam")
option = tk.OptionMenu(root, var, "Webcam", "Pre-existing Video")
option.grid(row=len(exercises)+2, column=0, padx=10, pady=5)

btn_file = tk.Button(root, text="Select Video File", command=select_video_file)
btn_file.grid(row=len(exercises)+3, column=0, padx=10, pady=5)

root.mainloop()
