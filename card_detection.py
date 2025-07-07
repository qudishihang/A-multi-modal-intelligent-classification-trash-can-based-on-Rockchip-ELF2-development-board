import tkinter as tk
import cv2
import os
import numpy as np
import time
import threading
import wave
import audioop
import struct
import io
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Path configuration
KNOWN_CARDS_FOLDER = "/home/elf/Desktop/q1"  # Known card folder
NEW_IMAGE_PATH = "/home/elf/Desktop/pic.jpg"  # Path to save captured photo

# Garbage categories mapping
garbage_mapping = {
    "罐头": "可回收垃圾",
    "旧衣服": "可回收垃圾",
    "甘蔗": "厨余垃圾",
    "蛋糕": "厨余垃圾",
    "骨头": "厨余垃圾",
    "蛋壳": "厨余垃圾",
    "菜叶": "厨余垃圾",
    "梨": "厨余垃圾",
    "发芽土豆": "厨余垃圾",
    "草莓": "厨余垃圾",
    "面包": "厨余垃圾",
    "番茄酱": "厨余垃圾",
    "葱": "厨余垃圾",
    "橙皮": "厨余垃圾",
    "香蕉皮": "厨余垃圾",
    "豌豆荚": "厨余垃圾",
    "蘑菇": "厨余垃圾",
    "辣椒皮": "厨余垃圾",
    "洋葱": "厨余垃圾",
    "西瓜": "厨余垃圾",
    "苹果核": "厨余垃圾",
    "蟹壳": "厨余垃圾",
    "鱼骨": "厨余垃圾",
    "西红柿": "厨余垃圾",
    "巧克力": "厨余垃圾",
    "饼干": "厨余垃圾",
    "玉米": "厨余垃圾",
    "虾": "厨余垃圾",
    "茄子": "厨余垃圾",
    "塑料瓶": "可回收垃圾",
    "梳子": "可回收垃圾",
    "铁锅": "可回收垃圾",
    "牙刷": "可回收垃圾",
    "纸盒": "可回收垃圾",
    "书": "可回收垃圾",
    "锁": "可回收垃圾",
    "牙膏皮": "可回收垃圾",
    "纸袋": "可回收垃圾",
    "手提包": "可回收垃圾",
    "鞋子": "可回收垃圾",
    "雨伞": "可回收垃圾",
    "勺子": "可回收垃圾",
    "塑料篮子": "可回收垃圾",
    "玩偶": "可回收垃圾",
    "易拉罐": "可回收垃圾",
    "玻璃瓶": "可回收垃圾",
    "牛奶盒": "可回收垃圾",
    "玻璃壶": "可回收垃圾",
    "镜子": "可回收垃圾",
    "帽子": "可回收垃圾",
    "报纸": "可回收垃圾",
    "夹子": "可回收垃圾",
    "垃圾桶": "可回收垃圾",
    "罐子": "可回收垃圾",
    "旧玩具": "可回收垃圾",
    "电池": "有害垃圾",
    "油漆桶": "有害垃圾",
    "调色板": "有害垃圾",
    "注射器": "有害垃圾",
    "创可贴": "有害垃圾",
    "药片": "有害垃圾",
    "香水瓶": "有害垃圾",
    "蓄电池": "有害垃圾",
    "油漆": "有害垃圾",
    "农药瓶": "有害垃圾",
    "水银体温计": "有害垃圾",
    "医用手套": "有害垃圾",
    "荧光棒": "有害垃圾",
    "医用棉签": "有害垃圾",
    "酒精": "有害垃圾",
    "水彩笔": "有害垃圾",
    "胶囊": "有害垃圾",
    "杀虫剂": "有害垃圾",
    "打火机": "有害垃圾",
    "化妆品": "有害垃圾",
    "煤气罐": "有害垃圾",
    "发胶": "有害垃圾",
    "口服液瓶子": "有害垃圾",
    "荧光灯": "有害垃圾",
    "蚊香片": "有害垃圾",
    "消毒液": "有害垃圾",
    "纱布": "有害垃圾",
    "坛子": "其他垃圾",
    "卫生纸": "其他垃圾",
    "一次性筷子": "其他垃圾",
    "扫把": "其他垃圾",
    "瓦片": "其他垃圾",
    "烟蒂": "其他垃圾",
    "砖块": "其他垃圾",
    "盘子": "其他垃圾",
    "陶瓷碗": "其他垃圾",
    "化妆刷": "其他垃圾",
    "板凳": "其他垃圾",
    "浴缸": "其他垃圾",
    "渣土": "其他垃圾",
    "尿片": "其他垃圾",
    "桃核": "其他垃圾",
    "西梅核": "其他垃圾",
    "砧板": "其他垃圾",
    "宠物粪便": "其他垃圾",
    "木梳子": "其他垃圾",
    "贝壳": "其他垃圾",
    "花瓶": "其他垃圾",
    "马桶": "其他垃圾",
    "杯子": "其他垃圾",
    "花盆": "其他垃圾",
    "篮球": "其他垃圾",
    "海绵": "其他垃圾",
    "一次性餐盒":" 其他垃圾"
}

KITCHEN_WASTE_PIN = 99    # Kitchen waste GPIO pin
RECYCLABLE_WASTE_PIN = 107  # Recyclable waste GPIO pin
HAZARDOUS_WASTE_PIN = 115  # Hazardous waste GPIO pin
OTHER_WASTE_PIN = 123     # Other waste GPIO pin

# PWM parameters
PWM_PERIOD = 0.02  # 20ms period (50Hz)
INITIAL_DUTY = 0.05  # Initial duty cycle 2.5%
FINAL_DUTY = 0.10    # Final duty cycle 5%

# GPIO control base path
GPIO_BASE_PATH = "/sys/class/gpio"

# Global variable to store the active PWM thread
current_pwm_thread = None

# GPIO control functions
def export_gpio(pin):
    """Export GPIO pin."""
    export_path = os.path.join(GPIO_BASE_PATH, "export")
    if not os.path.exists(os.path.join(GPIO_BASE_PATH, f"gpio{pin}")):
        try:
            with open(export_path, "w") as f:
                f.write(str(pin))
            time.sleep(0.1)  # Wait for the system to create the directory
            print(f"GPIO{pin} exported successfully")
        except Exception as e:
            print(f"Failed to export GPIO{pin}: {str(e)}")
            return False
    return True

def unexport_gpio(pin):
    """Unexport GPIO pin."""
    unexport_path = os.path.join(GPIO_BASE_PATH, "unexport")
    try:
        with open(unexport_path, "w") as f:
            f.write(str(pin))
        print(f"GPIO{pin} unexported successfully")
    except Exception as e:
        print(f"Failed to unexport GPIO{pin}: {str(e)}")

def set_gpio_direction(pin, direction):
    """Set GPIO direction (in/out)."""
    direction_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "direction")
    try:
        with open(direction_path, "w") as f:
            f.write(direction)
        return True
    except Exception as e:
        print(f"Failed to set GPIO{pin} direction: {str(e)}")
        return False

def set_gpio_value(pin, value):
    """Set GPIO output value (0/1)."""
    value_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "value")
    try:
        with open(value_path, "w") as f:
            f.write("1" if value else "0")
        return True
    except Exception as e:
        print(f"Failed to set GPIO{pin} value: {str(e)}")
        return False

def setup_gpio():
    """Initialize all GPIO pins."""
    pins = [KITCHEN_WASTE_PIN, RECYCLABLE_WASTE_PIN, HAZARDOUS_WASTE_PIN, OTHER_WASTE_PIN]
    for pin in pins:
        if export_gpio(pin):
            if set_gpio_direction(pin, "out"):
                set_gpio_value(pin, 0)  # Initialize to low level
                print(f"GPIO{pin} initialized successfully")
            else:
                print(f"Failed to set GPIO{pin} direction")
        else:
            print(f"Failed to export GPIO{pin}")

def cleanup_gpio():
    """Clean up all GPIO states."""
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
    PWM control thread function.
    :param pin: GPIO pin to control.
    :param initial_duty: Initial duty cycle.
    :param final_duty: Final duty cycle.
    :param duration: Duration for the initial duty cycle (seconds).
    """
    global current_pwm_thread
    
    try:
        print(f"Starting PWM signal output on GPIO{pin}")
        
        # Phase 1: Initial duty cycle
        start_time = time.time()
        while time.time() - start_time < duration:
            # High-level time
            high_time = PWM_PERIOD * initial_duty
            set_gpio_value(pin, 1)
            time.sleep(high_time)
            
            # Low-level time
            low_time = PWM_PERIOD * (1 - initial_duty)
            set_gpio_value(pin, 0)
            time.sleep(low_time)
        
        # Phase 2: Final duty cycle
        while current_pwm_thread == threading.current_thread():
            # High-level time
            high_time = PWM_PERIOD * final_duty
            set_gpio_value(pin, 1)
            time.sleep(high_time)
            
            # Low-level time
            low_time = PWM_PERIOD * (1 - final_duty)
            set_gpio_value(pin, 0)
            time.sleep(low_time)
    
    except Exception as e:
        print(f"PWM control error: {str(e)}")
    finally:
        try:
            set_gpio_value(pin, 0)  # Ensure the final state is low level
            print(f"PWM control on GPIO{pin} ended")
        except:
            pass

def start_pwm_for_category(category):
    """
    Start PWM control for the specified garbage category.
    :param category: Garbage category.
    """
    global current_pwm_thread
    
    # Stop the current PWM thread
    if current_pwm_thread and current_pwm_thread.is_alive():
        current_pwm_thread = None  # Notify the thread to exit
        time.sleep(0.1)  # Wait for the thread to exit
    
    # Select the corresponding GPIO pin based on the garbage category
    if category == "Kitchen waste":
        pin = KITCHEN_WASTE_PIN
        print("Controlling kitchen waste GPIO pin (GPIO17)")
    elif category == "Recyclable waste":
        pin = RECYCLABLE_WASTE_PIN
        print("Controlling recyclable waste GPIO pin (GPIO18)")
    elif category == "Hazardous waste":
        pin = HAZARDOUS_WASTE_PIN
        print("Controlling hazardous waste GPIO pin (GPIO27)")
    elif category == "Other waste":
        pin = OTHER_WASTE_PIN
        print("Controlling other waste GPIO pin (GPIO22)")
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

def load_images_from_folder(folder):
    """Load known cards from the folder."""
    images = []
    filenames = []
    
    for filename in sorted(os.listdir(folder)):
        filepath = os.path.join(folder, filename)
        try:
            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img is not None:
                img = preprocess_image(img)
                images.append(img)
                # Only keep the filename (without extension) as the identifier
                filenames.append(os.path.splitext(filename)[0])
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
    
    return images, filenames

def preprocess_image(img):
    """Image preprocessing."""
    h, w = img.shape[:2]
    if max(h, w) > 800:
        scale = 800 / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l,a,b)), cv2.COLOR_LAB2BGR)

def extract_features(img):
    """Feature extraction."""
    orb = cv2.ORB_create(nfeatures=500)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp, des = orb.detectAndCompute(gray, None)
    
    hist = cv2.calcHist([img], [0,1,2], None, [8,8,8], [0,256]*3)
    hist = cv2.normalize(hist, hist).flatten()
    
    return kp, des, hist

def find_matching_card(known_cards, new_img):
    """Card matching."""
    kp_new, des_new, hist_new = extract_features(new_img)
    best_match = (-1, 0)
    
    for i, card in enumerate(known_cards):
        kp_card, des_card, hist_card = extract_features(card)
        
        if des_card is not None and des_new is not None:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des_card, des_new)
            match_score = len(matches)/100
            hist_score = cv2.compareHist(hist_card, hist_new, cv2.HISTCMP_CORREL)
            total_score = match_score * 0.6 + hist_score * 0.4
            
            if total_score > best_match[1]:
                best_match = (i, total_score)
    
    return best_match

def take_photo():
    """Capture photo."""
    print("\nCapturing photo...")
    os.system('DISPLAY=:0.0 gst-launch-1.0 v4l2src device=/dev/video11 num-buffers=1 ! '
             'video/x-raw,format=NV12,width=640,height=480 ! '
             'mppjpegenc ! filesink location=' + NEW_IMAGE_PATH)
    
    # Check if the photo is successfully saved
    if not os.path.exists(NEW_IMAGE_PATH):
        print("Photo capture failed!")
        return None
    
    img = cv2.imread(NEW_IMAGE_PATH, cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to load the photo!")
        return None
    
    return preprocess_image(img)

def classify_and_control_gpio(garbage_name):
    """
    Classify and control GPIO based on garbage name.
    :param garbage_name: Name of the garbage.
    """
    if not garbage_name:
        print("No valid garbage name recognized")
        return
    
    # Find the garbage category
    category = garbage_mapping.get(garbage_name)
    
    if category:
        print(f"Recognition result: {garbage_name} -> {category}")
        start_pwm_for_category(category)
    else:
        print(f"No garbage category found for {garbage_name}")

def draw_chinese_text(image, text, position, font_size=20, font_path="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", color=(255, 0, 0)):
    """Draw Chinese text on the image."""
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    font = ImageFont.truetype(font_path, font_size)
    
    draw = ImageDraw.Draw(pil_image)
    
    draw.text(position, text, font=font, fill=color)
    
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# Global log variable
log_message = None


def update_log(message):
    """
    Update log information on the GUI.
    """
    global log_message
    log_message.set(message)  # Update the content displayed in the Label
    root.update_idletasks()   # Refresh the GUI


### Main button logic
def take_photo_and_classify():
    """
    Button functionality: Capture photo and classify.
    """
    update_log("Capture photo and classify functionality started...")
    try:

        # Capture photo
        new_img = take_photo()
        if new_img is None:
            update_log("Error", "Photo capture failed!")
            return

        # Match card
        update_log("Starting card matching...")
        match_idx, score = find_matching_card(known_cards, new_img)

        # Process matching result
        if match_idx != -1 and score > 0.2:
            garbage_name = filenames[match_idx]
            update_log(f"Match successful: {garbage_name} (Score: {score:.2f})")

            image_path = NEW_IMAGE_PATH
            image = cv2.imread(image_path)
            text = f"{garbage_name}"
            position = (50, 50)
            font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
            color = (255, 0, 0)

            image_with_text = draw_chinese_text(image, text, position, 20, font_path, color)
            result_path = os.path.splitext(image_path)[0] + "_result.jpg"
            cv2.imwrite(result_path, image_with_text)
            subprocess.Popen(["xdg-open", result_path])

            classify_and_control_gpio(garbage_name)
            time.sleep(5)
            os.system("pkill -f eog")
            update_log("Completed", f"Match successful: {garbage_name}")
        else:
            update_log(f"No matching card found (Highest score: {score:.2f})")
            update_log("Result", "No matching card found")
    except Exception as e:
        update_log("Error", f"Program runtime error: {str(e)}")

def cleanup_and_exit():
    """
    Button functionality: Clean up GPIO and exit the program.
    """
    try:
        cleanup_gpio()
        update_log("GPIO state cleaned up, exiting program")
        root.destroy()  # Close the Tkinter window
    except Exception as e:
        update_log("Error", f"Failed to clean up GPIO: {str(e)}")

if __name__ == "__main__":
    # Initialize GPIO
    setup_gpio()
    # Load known card library
    print("Loading card database...")
    known_cards, filenames = load_images_from_folder(KNOWN_CARDS_FOLDER)
    if not known_cards:
        print("Error", "No known cards loaded!")
        exit()

    print(f"{len(known_cards)} known cards loaded")
    
    # Create the Tkinter GUI
    root = tk.Tk()
    root.title("Card-based Garbage Classification System")
    root.geometry("4000x3000")
    
    # Define log variable
    log_message = tk.StringVar()
    log_message.set("Welcome to the Card-based Garbage Classification System")

    # Log display area
    log_label = tk.Label(root, textvariable=log_message, font=("Arial", 30), fg="black", wraplength=350, justify="left")
    log_label.pack(pady=20)

    # Create buttons
    btn_classify = tk.Button(root, text="Capture and Classify", command=take_photo_and_classify, font=("Arial", 50), fg="white", bg="green")
    btn_classify.pack(pady=20)

    btn_exit = tk.Button(root, text="Clean and Exit", command=cleanup_and_exit, font=("Arial", 50), fg="white", bg="red")
    btn_exit.pack(pady=20)

    # Start the Tkinter main loop
    root.mainloop()
