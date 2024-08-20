from django.shortcuts import render
from .forms import ParkingImageForm
import cv2
import numpy as np
import pytesseract
from ultralytics import YOLO
import re


# Укажите путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# Загрузка обученной модели YOLO
model = YOLO('best.pt')

def detect_plates(src):
    predictions = model.predict(src, verbose=False)
    results = []

    for prediction in predictions:
        for box in prediction.boxes:
            det_confidence = box.conf.item()
            if det_confidence < 0.6:
                continue
            coords = [int(position) for position in (box.xyxy.view(1, 4)).tolist()[0]]
            results.append(coords)

    return results

def crop(img, coords):
    cropped = img[coords[1]:coords[3], coords[0]:coords[2]]
    return cropped

def preprocess_image(img):
    normalize = cv2.normalize(img, np.zeros((img.shape[0], img.shape[1])), 0, 255, cv2.NORM_MINMAX)
    denoise = cv2.fastNlMeansDenoisingColored(normalize, h=10, hColor=10, templateWindowSize=7, searchWindowSize=15)
    grayscale = cv2.cvtColor(denoise, cv2.COLOR_BGR2GRAY)
    threshold = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshold

def ocr_plate(src):
    preprocessed = preprocess_image(src)
    custom_config = r'--oem 3 --psm 8'
    text = pytesseract.image_to_string(preprocessed, config=custom_config)
    plate_text_filtered = re.sub(r"[^A-Z0-9- ]", "", text).strip("- ")
    return plate_text_filtered

def ocr_plates(src, det_predictions):
    results = []

    for det_prediction in det_predictions:
        plate_region = crop(src, det_prediction)
        plate_text = ocr_plate(plate_region)
        results.append(plate_text)

    return results

def get_plates(src):
    det_predictions = detect_plates(src)
    ocr_predictions = ocr_plates(src, det_predictions)
    
    return ocr_predictions









# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image
# from ultralytics import YOLO

# # Укажите путь к Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# # Загрузка обученной модели YOLO
# model = YOLO('best.pt')


# def detect_license_plate(image):
#         # Преобразование изображения в формат, подходящий для OpenCV
#     nparr = np.frombuffer(image.read(), np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#  # Детекция с помощью YOLO
#     results = model(img)

#     recognized_numbers = []

#      # Проверка на наличие детекций
#     if results and len(results) > 0:
#         for result in results:
#             # Извлечение bounding boxes из результатов
#             boxes = result.boxes

#             for box in boxes:
#                 # Извлечение координат xyxy
#                 x1, y1, x2, y2 = box.xyxy[0].tolist()[:4]  # Координаты ограничивающего прямоугольника
#                 x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])  # Преобразование в целые числа
#                 cropped_image = img[y1:y2, x1:x2]
#                 preprocessed_image = preprocess_image(cropped_image)
#                 text = recognize_text(preprocessed_image)
#                   # Добавление текста в список распознанных номеров, если он не пуст
#                 if text:
#                     recognized_numbers.append(text)

#         # Возвращаем распознанные номера в одну строку
#         print(recognized_numbers)
#     return recognized_numbers if recognized_numbers else ["No license plates detected."]

# def preprocess_image(image):
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return thresh_image

# # def recognize_text(image):
# #     text = pytesseract.image_to_string(image, config='--psm 8')
# #     return text.strip()



# # def preprocess_image(image):
# #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #     # Увеличение контрастности с помощью адаптивного гистограммы
# #     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
# #     enhanced_image = clahe.apply(gray_image)
# #     # Применение гауссового размытия для уменьшения шума
# #     blurred_image = cv2.GaussianBlur(enhanced_image, (5, 5), 0)
# #     # Пороговая обработка
# #     _, thresh_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# #     return thresh_image

# def recognize_text(image):
#     # Используйте '--oem 3' для лучшего OCR движка и '--psm 7' для одиночной линии текста
#     config = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
#     text = pytesseract.image_to_string(image, config=config)
#     return text.strip()



