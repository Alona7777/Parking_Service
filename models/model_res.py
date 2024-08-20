from ultralytics import YOLO


# path to your car picture
img = '/Users/ALONA/Desktop/Go_IT/HW/Data Science/Data_Science/Number_plate_Recognition/License_Plate_Recognition/valid/images/004fddebf0ac943c_jpg.rf.b45c6ee8fc3320b2d7dac7dc76aacad1.jpg'

model = YOLO('models/best.pt')


results = model(img)
for result in results:
    result.show()

