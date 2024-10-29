from paddleocr import PaddleOCR
from ultralytics import YOLO
import cv2
import numpy as np


ocr = PaddleOCR(use_angle_cls=True, lang='en')
model = YOLO('best.pt')

def detect_and_recognize_license_plates(image):
    results = model.predict(image)

    recognized_texts = []
    annotated_image = image.copy()

    if results and len(results) > 0:
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist()[:4])
                cropped_image = image[y1:y2, x1:x2]

                ocr_result = ocr.ocr(cropped_image, cls=True)
            
                for line in ocr_result:
                    if line:
                        for word_info in line:
                            recognized_texts.append(word_info[1][0])

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


