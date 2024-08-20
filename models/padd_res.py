from paddleocr import PaddleOCR, draw_ocr
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np

# Инициализация OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Загрузка изображения и модели YOLO
image_path = '/Users/ALONA/Desktop/Go_IT/HW/Data Science/Data_Science/Number_plate_Recognition/License_Plate_Recognition/valid/images/00b6f96c840767fa_jpg.rf.ee1edf91f58203d50b54a53454296a1e.jpg'
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Применение YOLO для детекции
model = YOLO('models/best.pt')
results = model.predict(image_path)

# Функция для извлечения области интереса (ROI) из изображения по координатам
def extract_roi(image, bbox):
    x1, y1, x2, y2 = bbox
    return image[y1:y2, x1:x2]

# Применение OCR к каждому найденному bounding box
for result in results:
    boxes = result.boxes
    for box in boxes:
        # Извлечение координат xyxy
        x1, y1, x2, y2 = box.xyxy[0].tolist()[:4]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cropped_image = image[y1:y2, x1:x2]

        # Применение OCR к региону интереса
        ocr_result = ocr.ocr(cropped_image, cls=True)

        # Обработка результатов OCR
        for line in ocr_result:
            for word_info in line:
                print(f"Текст: {word_info[1][0]}, Координаты: {word_info[0]}")

        # Отображение результата на изображении (опционально)
        boxes = [elements[0] for elements in ocr_result[0]]
        pairs = [elements[1] for elements in ocr_result[0]]
        txts = [pair[0] for pair in pairs]
        scores = [pair[1] for pair in pairs]

        # Прорисовка результатов
        font_path = '/Library/Fonts/Arial.ttf'
        im_show = draw_ocr(cropped_image, boxes, txts, scores, font_path=font_path)
        im_show = Image.fromarray(im_show)
        im_show.save(f'result_image_{x1}_{y1}.jpg')
        im_show.show()


