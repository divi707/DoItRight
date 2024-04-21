import tkinter as tk
from tkinter import messagebox
import subprocess

# Function to run main.py
def run_main():
    subprocess.call(["python", "main.py"])

# Function to run pose_classification.py
def run_pose_classification():
    subprocess.call(["python", "pose_classification.py"])

# Create the main application window
root = tk.Tk()
root.title("Select File to Run")

# Create a label for file selection
label = tk.Label(root, text="Select what you want to do")
label.pack()

# Create buttons to run main.py and pose_classification.py
btn_main = tk.Button(root, text="Rep Counter", command=run_main)
btn_main.pack()

btn_classification = tk.Button(root, text="Pose classification", command=run_pose_classification)
btn_classification.pack()

# Start the GUI application
root.mainloop()
