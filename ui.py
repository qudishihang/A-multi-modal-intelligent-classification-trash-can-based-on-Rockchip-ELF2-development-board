import tkinter as tk
import subprocess
import sys

def run_selected_script(script_path):
    """Close the current program and run the selected Python file"""
    try:
        # Use the current Python interpreter to run the selected file
        subprocess.run([sys.executable, script_path])
    except Exception as e:
        print(f"Error occurred while running the script {script_path}: {e}")

# Create the main window
root = tk.Tk()
root.title("Smart Garbage Classification")
root.geometry("4000x3000")

# Create a label for the prompt
label_prompt = tk.Label(root, text="Please select the operation mode:", font=("Arial", 30), pady=20)
label_prompt.pack()

# Create a container for buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=20)

# Button 1: Run the first Python file
btn_script_1 = tk.Button(frame_buttons, text="Card Garbage Classification", font=("Arial", 50),
                         command=lambda: run_selected_script("picture6.py"))
btn_script_1.pack(pady=10)

# Button 2: Run the second Python file
btn_script_2 = tk.Button(frame_buttons, text="Voice Garbage Classification", font=("Arial", 50),
                         command=lambda: run_selected_script("speech7.py"))
btn_script_2.pack(pady=10)

# Button 3: Run the third Python file
btn_script_3 = tk.Button(frame_buttons, text="Physical Garbage Classification", font=("Arial", 50),
                         command=lambda: run_selected_script("testmain3.py"))
btn_script_3.pack(pady=10)

# Run the main loop
root.mainloop()
