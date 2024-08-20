from ultralytics import YOLO
import cv2
import numpy as np

# Загрузка обученной модели YOLO
model = YOLO('best.pt')

def detect_license_plate(image):
    # Преобразование изображения в формат, подходящий для OpenCV
    nparr = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Детекция с помощью YOLO
    results = model(img)

    # Проверка на наличие детекций
    if len(results.xyxy) > 0 and len(results.xyxy[0]) > 0:
        bboxes = results.xyxy[0].numpy()  # Получение координат ограничивающих рамок

        recognized_numbers = []
        for bbox in bboxes:
            x1, y1, x2, y2, conf, cls = bbox
            cropped_image = img[int(y1):int(y2), int(x1):int(x2)]
            preprocessed_image = preprocess_image(cropped_image)
            text = recognize_text(preprocessed_image)
            recognized_numbers.append(text)

        return recognized_numbers
    else:
        # Если нет детекций, возвращаем пустой список или сообщение
        return []

def preprocess_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh_image

def recognize_text(image):
    text = pytesseract.image_to_string(image, config='--psm 8')
    return text.strip()




# Process results list
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()  # display to screen
    result.save(filename="result.jpg")  # save to disk
