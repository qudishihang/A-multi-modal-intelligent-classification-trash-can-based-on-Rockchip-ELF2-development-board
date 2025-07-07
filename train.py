from ultralytics import YOLO

# Load the model
model = YOLO("yolov8n.pt")  # Load the pre-trained model

if __name__ == '__main__':
    # Train the model
    results = model.train(
        data=r'C:\Users\123\Downloads\GarbageDetection\data.yaml',  # Path to the dataset configuration file
        epochs=250,  # Number of training epochs
        batch=4  # Batch size for training
    )
