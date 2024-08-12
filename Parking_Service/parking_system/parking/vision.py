import cv2
import numpy as np
import pytesseract
from PIL import Image


def detect_license_plate(image_path):
    # Зчитування зображення
    image = cv2.imread(r"C:\Users\magen\Downloads\filenomer.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Використання OpenCV для виявлення контурів
    edged = cv2.Canny(gray, 30, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    screenCnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        return None

    # Маскування зображення та виділення області з номерним знаком
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    new_image = cv2.bitwise_and(image, image, mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

    # Використання Tesseract для розпізнавання тексту
    text = pytesseract.image_to_string(cropped, config='--psm 11')
    return text.strip()
