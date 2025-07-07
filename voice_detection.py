import json
import os
import subprocess
import wave
import audioop
import struct
import numpy as np
from vosk import Model, KaldiRecognizer
from pypinyin import pinyin, Style
import Levenshtein
import time
import io
import threading
import tkinter as tk

# Define garbage type mapping
garbage_mapping = {
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

# Added similarity threshold
SIMILARITY_THRESHOLD = 0.6

# Define fixed GPIO pins
KITCHEN_WASTE_PIN = 99   # Kitchen waste pin
RECYCLABLE_WASTE_PIN = 107 # Recyclable waste pin
HAZARDOUS_WASTE_PIN = 115  # Hazardous waste pin
OTHER_WASTE_PIN = 123      # Other waste pin

# PWM parameters
PWM_PERIOD = 0.02  # 20ms period (50Hz)
INITIAL_DUTY = 0.05  # Initial duty cycle 2.5%
FINAL_DUTY = 0.10    # Final duty cycle 5%

# GPIO control base path
GPIO_BASE_PATH = "/sys/class/gpio"

# Global variable to store the current active PWM thread
current_pwm_thread = None

def export_gpio(pin):
    """Export GPIO pin"""
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
    """Unexport GPIO pin"""
    unexport_path = os.path.join(GPIO_BASE_PATH, "unexport")
    try:
        with open(unexport_path, "w") as f:
            f.write(str(pin))
        print(f"GPIO{pin} unexported successfully")
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

        # First stage: Initial duty cycle
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

        # Second stage: Final duty cycle
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
        print(f"PWM control error: {str(e)}")
    finally:
        try:
            set_gpio_value(pin, 0)  # Ensure low level at the end
            print(f"PWM control ended on GPIO{pin}")
        except:
            pass

def start_pwm_for_category(category):
    """
    Start PWM control for the specified garbage category
    :param category: Garbage category
    """
    global current_pwm_thread

    # Stop the current PWM thread
    if current_pwm_thread and current_pwm_thread.is_alive():
        current_pwm_thread = None  # Notify the thread to exit
        time.sleep(0.1)  # Wait for the thread to exit

    # Select GPIO pin based on garbage category
    if category == "Kitchen Waste":
        pin = KITCHEN_WASTE_PIN
        print("Controlling kitchen waste pin (GPIO17)")
    elif category == "Recyclable Garbage":
        pin = RECYCLABLE_WASTE_PIN
        print("Controlling recyclable garbage pin (GPIO18)")
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

def record_audio(duration=5, output_file="temp.wav"):
    """
    Record audio using arecord command
    :param duration: Recording duration (seconds)
    :param output_file: Output filename
    :return: True if recording succeeds, False otherwise
    """
    # Delete any existing old file
    if os.path.exists(output_file):
        os.remove(output_file)

    # Build the recording command
    command = [
        "arecord",
        "-D", "hw:rockchipnau8822,0",  # Specify audio device
        "-d", str(duration),            # Recording duration
        "-f", "cd",                     # CD quality format (44.1kHz, 16-bit, stereo)
        "-t", "wav",                    # WAV format
        output_file                     # Output file
    ]

    print("Starting audio recording...")
    try:
        # Execute the recording command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # Check the recording result
        if process.returncode != 0:
            print(f"Recording failed: {stderr.decode('utf-8')}")
            return False

        # Check if the file is valid
        if not os.path.exists(output_file) or os.path.getsize(output_file) < 1024:
            print("Recorded file is invalid or too small")
            return False

        print(f"Recording succeeded, file saved as: {output_file}")
        return True
    except Exception as e:
        print(f"Error during recording: {str(e)}")
        return False

def convert_audio_in_memory(input_data):
    """
    Pure Python implementation for audio format conversion.
    Converts 44.1kHz stereo audio to 16kHz mono.
    :param input_data: Original audio data (bytes)
    :return: Converted audio data (bytes)
    """
    try:
        # Wrap the input data as a file object
        with io.BytesIO(input_data) as input_stream:
            # Read the original audio file
            with wave.open(input_stream, 'rb') as wav_in:
                n_channels = wav_in.getnchannels()
                sample_width = wav_in.getsampwidth()
                frame_rate = wav_in.getframerate()
                n_frames = wav_in.getnframes()
                frames = wav_in.readframes(n_frames)
                
                # Check if the format is supported
                if sample_width != 2:  # Only support 16-bit audio
                    print(f"Unsupported sample width: {sample_width} bytes")
                    return None
                
                # Convert to mono (average the two channels)
                if n_channels == 2:
                    frames = audioop.tomono(frames, sample_width, 1, 1)
                
                # Resample to 16kHz (from 44.1kHz to 16kHz)
                # Simplest method: Sample extraction (44.1/16≈2.76, so take one sample every 2.76 samples)
                # More precise method: Linear interpolation
                target_rate = 16000
                ratio = frame_rate / target_rate
                
                # Create a buffer for the new audio data
                new_frames = bytearray()
                
                # Use linear interpolation for resampling
                for i in range(int(n_frames / ratio)):
                    # Compute the original position
                    pos = i * ratio
                    idx1 = int(pos)
                    idx2 = min(idx1 + 1, n_frames - 1)
                    
                    # Get adjacent samples
                    sample1 = struct.unpack('<h', frames[idx1 * sample_width:idx1 * sample_width + 2])[0]
                    sample2 = struct.unpack('<h', frames[idx2 * sample_width:idx2 * sample_width + 2])[0]
                    
                    # Perform linear interpolation
                    frac = pos - idx1
                    interpolated = sample1 + frac * (sample2 - sample1)
                    interpolated = int(interpolated)
                    
                    # Restrict to 16-bit range
                    interpolated = max(min(interpolated, 32767), -32768)
                    
                    # Add to the new frames
                    new_frames.extend(struct.pack('<h', interpolated))
                
                # Create the output WAV file
                with io.BytesIO() as output_stream:
                    with wave.open(output_stream, 'wb') as wav_out:
                        wav_out.setnchannels(1)  # Mono
                        wav_out.setsampwidth(2)  # 16-bit
                        wav_out.setframerate(target_rate)
                        wav_out.writeframes(new_frames)
                    
                    # Return the converted data
                    return output_stream.getvalue()
    
    except Exception as e:
        print(f"Audio conversion error: {str(e)}")
        return None

def recognize_speech(audio_file="temp.wav"):
    """
    Use Vosk to recognize speech from an audio file
    :param audio_file: Path to the audio file
    :return: Recognized text content
    """
    # Check if the audio file exists
    if not os.path.exists(audio_file):
        print(f"Audio file does not exist: {audio_file}")
        return ""

    # Load Vosk Chinese model (use the model path on the development board)
    model_path = "/home/elf/Desktop/vosk-model-small-cn-0.22/vosk-model-small-cn-0.22"
    if not os.path.exists(model_path):
        print(f"Model path does not exist: {model_path}")
        return ""

    try:
        # Read the original audio data
        with open(audio_file, 'rb') as f:
            raw_data = f.read()

        # Convert to 16kHz mono
        converted_data = convert_audio_in_memory(raw_data)
        if not converted_data:
            print("Audio conversion failed")
            return ""

        # Create an in-memory audio file
        with io.BytesIO(converted_data) as audio_stream:
            # Load the model
            model = Model(model_path)

            # Read the converted audio
            wf = wave.open(audio_stream, 'rb')

            # Validate the audio format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                print(f"Converted audio format error: Channels={wf.getnchannels()}, Sample width={wf.getsampwidth()}")
                wf.close()
                return ""

            # Create recognizer
            rec = KaldiRecognizer(model, wf.getframerate())

            print("Starting speech recognition...")
            start_time = time.time()

            # Read audio data
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    pass

            # Get the final result
            result = json.loads(rec.FinalResult())
            text = result.get("text", "")

            # Remove spaces
            text = text.replace(" ", "")

            elapsed = time.time() - start_time
            print(f"Recognition complete, elapsed time: {elapsed:.2f} seconds")
            print(f"Recognition result: {text}")

            wf.close()
            return text

    except wave.Error as e:
        print(f"WAV file error: {str(e)}")
        return ""
    except Exception as e:
        print(f"Speech recognition failed: {str(e)}")
        return ""

def get_pinyin(text):
    """Get the pinyin string of the text"""
    return ''.join([item[0] for item in pinyin(text, style=Style.NORMAL)])

def calculate_similarity(input_pinyin, target_pinyin):
    """Calculate the similarity between two pinyin strings (0-1)"""
    distance = Levenshtein.distance(input_pinyin, target_pinyin)
    max_len = max(len(input_pinyin), len(target_pinyin))
    return (max_len - distance) / max_len if max_len > 0 else 1.0

def classify_garbage(garbage_name):
    """Classify garbage based on its name and control GPIO"""
    if not garbage_name:
        return "No valid content recognized"

    category = None

    if garbage_name in garbage_mapping:
        category = garbage_mapping[garbage_name]
    else:
        input_pinyin = get_pinyin(garbage_name)
        best_similarity = 0
        closest_match = None

        # Find the most similar garbage name
        for key in garbage_mapping.keys():
            key_pinyin = get_pinyin(key)
            similarity = calculate_similarity(input_pinyin, key_pinyin)

            if similarity > best_similarity:
                best_similarity = similarity
                closest_match = key

        # Evaluate match success based on the similarity threshold
        if best_similarity >= SIMILARITY_THRESHOLD:
            print(f"Closest garbage name: {closest_match}, Similarity: {best_similarity:.2f}")
            category = garbage_mapping[closest_match]
        else:
            print(f"Best match similarity: {best_similarity:.2f}, below threshold {SIMILARITY_THRESHOLD}")
            return "No matching garbage category found"

    # Control GPIO to output PWM signal
    if category:
        start_pwm_for_category(category)

    return category

# Global variable for updating the interface log
log_message = None

def update_log(message):
    """
    Update interface log information
    """
    global log_message
    log_message.set(message)  # Update content displayed in the Label
    root.update_idletasks()   # Refresh the interface

def start_record_and_classify():
    """
    Start recording and garbage classification
    """
    update_log("Starting audio recording...")

    def task():
        try:
            # 1. Record audio
            if record_audio(duration=2):
                update_log("Recording complete, performing speech recognition...")

                # 2. Recognize speech
                garbage_name = recognize_speech()
                if garbage_name:
                    update_log(f"Recognized garbage name: {garbage_name}\nClassifying...")
                    
                    # 3. Classify garbage
                    result = classify_garbage(garbage_name)
                    update_log(f"Garbage classification result: {result}")
                else:
                    update_log("No valid content recognized, please try again")
            else:
                update_log("Audio recording failed, please check the device")
        except Exception as e:
            print(f"Error occurred during program execution: {str(e)}")
        finally:
            print("")

    # Use thread to avoid blocking the main interface
    threading.Thread(target=task, daemon=True).start()

def cleanup_and_exit():
    """
    Clean up GPIO and exit program
    """
    try:
        cleanup_gpio()
        update_log("GPIO state cleaned up, program exited")
    finally:
        root.destroy()

if __name__ == "__main__":
    # Initialize GPIO
    setup_gpio()

    # Create Tkinter window
    root = tk.Tk()
    root.title("Speech Garbage Classification System")
    root.geometry("400x300")

    # Define log variable
    log_message = tk.StringVar()
    log_message.set("Welcome to the Speech Garbage Classification System")

    # Log display area
    log_label = tk.Label(root, textvariable=log_message, font=("Arial", 12), fg="black", wraplength=350, justify="left")
    log_label.pack(pady=20)

    # Create buttons
    btn_start = tk.Button(root, text="Start Recording and Classification", command=start_record_and_classify, font=("Arial", 12), fg="white", bg="blue")
    btn_start.pack(pady=20)

    btn_exit = tk.Button(root, text="Clean Up and Exit", command=cleanup_and_exit, font=("Arial", 12), fg="white", bg="red")
    btn_exit.pack(pady=20)

    # Start Tkinter main loop
    root.mainloop()
