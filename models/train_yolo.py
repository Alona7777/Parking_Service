from ultralytics import YOLO

def train_model():
    model = YOLO('yolov8s.pt')
    
    # Запустите процесс обучения
    model.train(
        data='/Users/ALONA/Desktop/Go_IT/HW/Data Science/Data_Science/Number_plate_Recognition/License_Plate_Recognition/data.yaml',
        imgsz= 640,                    # Размер изображений
        epochs=20,                     # Количество эпох
        # batch=16,                      # Размер батча, по умолчанию
        patience=10,                   # Количество эпох без улучшения для ранней остановки
        device="mps",                  # To enable training on Apple M1 and M2 chips
        name='YOLOv8s_license_plate'   # Имя эксперимента
)

if __name__ == "__main__":
    train_model()

# После выполнения этого скрипта графики будут сохранены в:
# runs/train/YOLOv8s_license_plate/  