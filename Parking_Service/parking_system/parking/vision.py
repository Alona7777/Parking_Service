from paddleocr import PaddleOCR
from ultralytics import YOLO
import cv2
import numpy as np

# Инициализация OCR и модели YOLO
ocr = PaddleOCR(use_angle_cls=True, lang='en')
model = YOLO('best.pt')

def detect_and_recognize_license_plates(image):
    # Применение YOLO для детекции
    results = model.predict(image)

    recognized_texts = []
    annotated_image = image.copy()

    # Применение OCR к каждому найденному bounding box
     # Проверка на наличие детекций
    if results and len(results) > 0:
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist()[:4])
                cropped_image = image[y1:y2, x1:x2]

                # Применение OCR к региону интереса
                ocr_result = ocr.ocr(cropped_image, cls=True)
                # Обработка результатов OCR
                for line in ocr_result:
                    if line:
                        for word_info in line:
                            recognized_texts.append(word_info[1][0])

                            # Аннотирование изображения (опционально)
                            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(annotated_image, word_info[1][0], (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    else:
                        text = "Not recognized"
                        recognized_texts.append(text)
                        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated_image, text, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return recognized_texts, annotated_image
    
    else:
        return "No license plates detected."



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


