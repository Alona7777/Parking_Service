from ultralytics import YOLO


# path to your car picture
img = '/Users/ALONA/Desktop/Go_IT/HW/Data Science/Data_Science/Number_plate_Recognition/License_Plate_Recognition/test/images/brightnessquandoi20_jpg.rf.5f2b75fb7ea702cd325b104c19f5fd36.jpg'

model = YOLO('models/best.pt')


results = model(img)
for result in results:
    result.show()


from paddleocr import PaddleOCR, draw_ocr
from PIL import Image

# Инициализация OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Используйте 'ch' для китайского, если нужно

# Применение OCR к изображению
img_path = 'path_to_your_image.jpg'
result = ocr.ocr(img_path, cls=True)

# Обработка результатов
for line in result:
    for word_info in line:
        print(f"Текст: {word_info[1][0]}, Координаты: {word_info[0]}")

# Отображение результата на изображении (опционально)
image = Image.open(img_path).convert('RGB')
boxes = [elements[0] for elements in result[0]]
pairs = [elements[1] for elements in result[0]]
txts = [pair[0] for pair in pairs]
scores = [pair[1] for pair in pairs]

# Прорисовка результатов
im_show = draw_ocr(image, boxes, txts, scores, font_path='path_to_font.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result_image.jpg')
im_show.show()

