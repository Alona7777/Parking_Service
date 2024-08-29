from ultralytics import YOLO


# path to your car picture
img = '/Users/ALONA/Desktop/Final_project/Parking_Service/parking_system/media/img_readme/0002a5b67e5f0909_jpg.rf.07ca41e79eb878b14032f650f34d0967.jpg'

model = YOLO('models/best.pt')


results = model(img)
for result in results:
    result.show()


# from paddleocr import PaddleOCR, draw_ocr
# from PIL import Image

# # Инициализация OCR
# ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Используйте 'ch' для китайского, если нужно

# # Применение OCR к изображению
# img_path = 'path_to_your_image.jpg'
# result = ocr.ocr(img_path, cls=True)

# # Обработка результатов
# for line in result:
#     for word_info in line:
#         print(f"Текст: {word_info[1][0]}, Координаты: {word_info[0]}")

# # Отображение результата на изображении (опционально)
# image = Image.open(img_path).convert('RGB')
# boxes = [elements[0] for elements in result[0]]
# pairs = [elements[1] for elements in result[0]]
# txts = [pair[0] for pair in pairs]
# scores = [pair[1] for pair in pairs]

# # Прорисовка результатов
# im_show = draw_ocr(image, boxes, txts, scores, font_path='path_to_font.ttf')
# im_show = Image.fromarray(im_show)
# im_show.save('result_image.jpg')
# im_show.show()

