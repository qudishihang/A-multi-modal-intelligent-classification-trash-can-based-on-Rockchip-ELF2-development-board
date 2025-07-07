import time
import sys
import os
from ultralytics import YOLO
import cv2
import numpy as np
import threading
import subprocess
import tkinter as tk
from rknn.api import RKNN

# Assuming Config contains category names or path configurations
class Config:
    # Path to save image and video detection results
    save_path = 'save_data'

    # Path of the used model
    model_path = 'models/best.pt'
    names = {0: 'recyclable waste', 1: "hazardous waste", 2: "kitchen waste", 3: "other waste"}
    CH_names = ['Recyclable Waste', 'Hazardous Waste', 'Kitchen Waste', 'Other Waste']

# Path configuration
NEW_IMAGE_PATH = "/home/elf/Desktop/pic.jpg"  # Path to save captured image

# GPIO pin configuration
KITCHEN_WASTE_PIN = 99    # Pin for kitchen waste
RECYCLABLE_WASTE_PIN = 107 # Pin for recyclable waste
HAZARDOUS_WASTE_PIN = 115  # Pin for hazardous waste
OTHER_WASTE_PIN = 123     # Pin for other waste

# PWM parameters
PWM_PERIOD = 0.02  # 20ms period (50Hz)
INITIAL_DUTY = 0.05  # Initial duty cycle 2.5%
FINAL_DUTY = 0.10    # Final duty cycle 5%

# Base path for GPIO control
GPIO_BASE_PATH = "/sys/class/gpio"

# Global variable to store the currently active PWM thread
current_pwm_thread = None

# GPIO control functions
def export_gpio(pin):
    """Export GPIO pin"""
    export_path = os.path.join(GPIO_BASE_PATH, "export")
    if not os.path.exists(os.path.join(GPIO_BASE_PATH, f"gpio{pin}")):
        try:
            with open(export_path, "w") as f:
                f.write(str(pin))
            time.sleep(0.1)  # Wait for the system to create the directory
            print(f"GPIO{pin} has been exported")
        except Exception as e:
            print(f"Failed to export GPIO{pin}: {str(e)}")
            return False
    return True

def unexport_gpio(pin):
    """Unexport GPIO pin"""
    unexport_path = os.path.join(GPIO_BASE_PATH, "unexport")
    try:
        with open(unexport_path, "w") as f:
            f.write(str(pin))
        print(f"GPIO{pin} has been unexported")
    except Exception as e:
        print(f"Failed to unexport GPIO{pin}: {str(e)}")

def set_gpio_direction(pin, direction):
    """Set GPIO direction (in/out)"""
    direction_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "direction")
    try:
        with open(direction_path, "w") as f:
            f.write(direction)
        return True
    except Exception as e:
        print(f"Failed to set direction for GPIO{pin}: {str(e)}")
        return False

def set_gpio_value(pin, value):
    """Set GPIO output value (0/1)"""
    value_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "value")
    try:
        with open(value_path, "w") as f:
            f.write("1" if value else "0")
        return True
    except Exception as e:
        print(f"Failed to set value for GPIO{pin}: {str(e)}")
        return False

def setup_gpio():
    """Initialize all GPIO pins"""
    pins = [KITCHEN_WASTE_PIN, RECYCLABLE_WASTE_PIN, HAZARDOUS_WASTE_PIN, OTHER_WASTE_PIN]
    for pin in pins:
        if export_gpio(pin):
            if set_gpio_direction(pin, "out"):
                set_gpio_value(pin, 0)  # Initialize to low level
                print(f"GPIO{pin} initialized successfully")
            else:
                print(f"Failed to set direction for GPIO{pin}")
        else:
            print(f"Failed to export GPIO{pin}")

def cleanup_gpio():
    """Clean up all GPIO states"""
    pins = [KITCHEN_WASTE_PIN, RECYCLABLE_WASTE_PIN, HAZARDOUS_WASTE_PIN, OTHER_WASTE_PIN]
    for pin in pins:
        try:
            set_gpio_value(pin, 0)  # Set to low level
            unexport_gpio(pin)      # Unexport
            print(f"GPIO{pin} cleaned up successfully")
        except Exception as e:
            print(f"Failed to clean up GPIO{pin}: {str(e)}")

def pwm_control(pin, initial_duty, final_duty, duration=3):
    """
    PWM control thread function
    :param pin: GPIO pin to control
    :param initial_duty: Initial duty cycle
    :param final_duty: Final duty cycle
    :param duration: Duration for the initial duty cycle (seconds)
    """
    global current_pwm_thread

    try:
        print(f"Starting PWM signal output on GPIO{pin}")

        # Phase 1: Initial duty cycle
        start_time = time.time()
        while time.time() - start_time < duration:
            # High level duration
            high_time = PWM_PERIOD * initial_duty
            set_gpio_value(pin, 1)
            time.sleep(high_time)

            # Low level duration
            low_time = PWM_PERIOD * (1 - initial_duty)
            set_gpio_value(pin, 0)
            time.sleep(low_time)

        # Phase 2: Final duty cycle
        while current_pwm_thread == threading.current_thread():
            # High level duration
            high_time = PWM_PERIOD * final_duty
            set_gpio_value(pin, 1)
            time.sleep(high_time)

            # Low level duration
            low_time = PWM_PERIOD * (1 - final_duty)
            set_gpio_value(pin, 0)
            time.sleep(low_time)

    except Exception as e:
        print(f"Error during PWM control: {str(e)}")
    finally:
        try:
            set_gpio_value(pin, 0)  # Ensure the last state is low level
            print(f"PWM control ended on GPIO{pin}")
        except:
            pass

def start_pwm_for_category(category):
    """
    Start PWM control for a specified garbage category
    :param category: Garbage category
    """
    global current_pwm_thread

    # Stop the current PWM thread
    if current_pwm_thread and current_pwm_thread.is_alive():
        current_pwm_thread = None  # Notify the thread to exit
        time.sleep(0.1)  # Wait for the thread to exit

    # Select the corresponding GPIO pin based on the garbage category
    if category == "Kitchen Waste":
        pin = KITCHEN_WASTE_PIN
        print("Controlling kitchen waste pin (GPIO17)")
    elif category == "Recyclable Waste":
        pin = RECYCLABLE_WASTE_PIN
        print("Controlling recyclable waste pin (GPIO18)")
    elif category == "Hazardous Waste":
        pin = HAZARDOUS_WASTE_PIN
        print("Controlling hazardous waste pin (GPIO27)")
    elif category == "Other Waste":
        pin = OTHER_WASTE_PIN
        print("Controlling other waste pin (GPIO22)")
    else:
        print(f"Unknown garbage category: {category}")
        return

    # Create and start a new PWM thread
    current_pwm_thread = threading.Thread(
        target=pwm_control,
        args=(pin, INITIAL_DUTY, FINAL_DUTY),
        daemon=True
    )
    current_pwm_thread.start()
    print(f"Started PWM control for {category} (GPIO{pin})")

def take_photo():
    """Function to take a photo"""
    print("\nTaking photo...")
    os.system('DISPLAY=:0.0 gst-launch-1.0 v4l2src device=/dev/video11 num-buffers=1 ! '
              'video/x-raw,format=NV12,width=640,height=480 ! '
              'mppjpegenc ! filesink location=' + NEW_IMAGE_PATH)

    # Check if the photo was successfully saved
    if not os.path.exists(NEW_IMAGE_PATH):
        print("Photo capture failed!")
        return None

    img = cv2.imread(NEW_IMAGE_PATH, cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to read the photo!")
        return None

    return img

class ImageClassifier:
    def __init__(self, model_path):
        """
        Initialize classifier and load RKNN model
        """
        self.rknn = RKNN()  # Initialize RKNN object
        self.model_path = model_path

        # Load the model
        print(f"[INFO] Loading RKNN model: {self.model_path}")
        ret = self.rknn.load_rknn(model_path)
        if ret != 0:
            print("[ERROR] Failed to load RKNN model!")
            exit(1)

        # Initialize RKNN runtime
        ret = self.rknn.init_runtime()
        if ret != 0:
            print("[ERROR] Failed to initialize RKNN runtime!")
            exit(1)

        print("[INFO] RKNN model loaded successfully")

    def classify_image(self, image_path):
        """
        Classify an image using the RKNN model
        """
        if not os.path.exists(image_path):
            print(f"[ERROR] Image path does not exist: {image_path}")
            return None

        print(f"[INFO] Processing image: {image_path}")

        # Load the image
        original_image = cv2.imread(image_path)
        if original_image is None:
            print(f"[ERROR] Failed to load the image: {image_path}")
            return None

        # Preprocess the image
        input_image = cv2.resize(original_image, (640, 480)) 
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension

        # Model inference
        t1 = time.time()
        outputs = self.rknn.inference(inputs=[input_image])
        t2 = time.time()
        print(f"[INFO] Detection time: {t2 - t1:.3f} seconds")

        # Parse output
        class_idx = np.argmax(outputs[0])  # Get classification result
        confidence = np.max(outputs[0])   # Get classification confidence
        class_name = Config.names[class_idx]  # Get category name from config
        chinese_class_name = Config.CH_names[class_idx]

        print(f"[RESULT] Category: {class_name}, Confidence: {confidence:.2f}")

        # Display result
        label = f"{class_name} ({confidence*100:.2f}%)"
        cv2.putText(original_image, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        result_path = os.path.splitext(image_path)[0] + "_result_rknn.jpg"
        cv2.imwrite(result_path, original_image)
        print(f"[INFO] Detection result saved: {result_path}")

        # Start corresponding GPIO control
        start_pwm_for_category(chinese_class_name)
        time.sleep(5)
        os.system("pkill -f eog")
        return {"class_name": class_name, "confidence": confidence}

    def __del__(self):
        """
        Clean up RKNN resources
        """
        self.rknn.release()
    
# Add global variable to update GUI logs
log_message = None

def update_log(message):
    """
    Update log information in the GUI
    """
    global log_message
    log_message.set(message)  # Update the content displayed in the Label
    root.update_idletasks()   # Refresh the GUI

def take_photo_and_classify():
    """
    Button function to take photo and classify
    """
    update_log("Starting photo capture...")
    try:
        # Capture photo
        new_img = take_photo()
        if new_img is None:
            update_log("Photo capture failed, exiting program")
        else:
            # Perform classification
            update_log("Performing classification...")
            results = classifier.classify_image(NEW_IMAGE_PATH)
            if results:
                update_log(f"Classification completed: {results['class_name']} ({results['confidence']})")
            else:
                update_log("No garbage detected meeting the criteria")
    finally:
        update_log("Photo capture and classification logic completed")

def cleanup_and_exit():
    """
    Button function to clean up GPIO and exit program
    """
    try:
        update_log("Cleaning up GPIO states...")
        cleanup_gpio()
        update_log("GPIO states cleaned up, exiting program")
    finally:
        root.destroy()  # Close Tkinter window

if __name__ == "__main__":
    # Initialize GPIO
    setup_gpio()

    # Configure model path
    MODEL_PATH = "/home/elf/Desktop/best.rknn"

    # Load classifier
    classifier = ImageClassifier(MODEL_PATH)
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("Physical Garbage Classification System")
    root.geometry("4000x3000")

    # Define log variable
    log_message = tk.StringVar()
    log_message.set("Welcome to the Physical Garbage Classification System")

    # Log display area
    log_label = tk.Label(root, textvariable=log_message, font=("Arial", 30), fg="black", wraplength=350, justify="left")
    log_label.pack(pady=20)

    # Create buttons
    btn_classify = tk.Button(root, text="Take Photo and Classify", command=take_photo_and_classify, font=("Arial", 50), fg="white", bg="green")
    btn_classify.pack(pady=20)

    btn_exit = tk.Button(root, text="Clean up and Exit", command=cleanup_and_exit, font=("Arial", 50), fg="white", bg="red")
    btn_exit.pack(pady=20)

    # Start Tkinter main loop
    root.mainloop()