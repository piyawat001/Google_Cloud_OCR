import io
import os
from google.cloud import vision_v1p3beta1 as vision
import cv2
import pandas as pd
import shutil

import os
    
# Setup google authen client key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api.json'

# Source path content all images
SOURCE_FOLDER = "img"

def recognize_license_plate(img_path):
    img = cv2.imread(img_path)
    # Get image size
    height, width = img.shape[:2]
    # Scale image
    img = cv2.resize(img, (800, int((height * 800) / width)))
    # Show the origin image
    cv2.imshow('Origin image', img)
    # Save the image to temp file
    output_path = img_path.replace(".jpg", "_output.jpg")
    cv2.imwrite(output_path, img)
    # Create google vision client
    client = vision.ImageAnnotatorClient()
    # Read image file
    with io.open(output_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    response2 = client.text_detection(image=image)
    texts = response2.text_annotations
    for logo in logos:
        print(logo.description)
        cv2.putText(img, logo.description, (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.imshow('Recognize & Draw', img)  
    i=0
    for text in texts:
        if i==0 :
            i=i+1
            license_plate = text.description
            print(license_plate)
            vertices = [(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices]
            cv2.rectangle(img, (vertices[0][0]-10, vertices[0][1]-10), (vertices[2][0]+10, vertices[2][1]+10), (0, 255, 0), 3)
            cv2.imshow('Recognize & Draw2', img)
            #cv2.waitKey(0)
    return license_plate
            
print('---------- Start recognize license plate --------')
path = SOURCE_FOLDER

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.jpg' in file:
            files.append(os.path.join(r, file))
            
results = []
for f in files:
    print(f)
    path = f
    license_plate = recognize_license_plate(path)
    license_plate_parts = license_plate.split()
    license_plate_number = license_plate_parts[0] if len(license_plate_parts) > 0 else ""
    license_plate_number2 = license_plate_parts[2] if len(license_plate_parts) > 2 else ""
    province = license_plate_parts[1] if len(license_plate_parts) > 1 else ""
    results.append((f, license_plate_number, license_plate_number2, province))

df = pd.DataFrame(results, columns=['Image', 'License Plate', 'Number', 'Province'])
df = df.set_index(['License Plate', 'Number', 'Province'])
print(df)
df.to_excel('license_plate_results.xlsx')

# สร้างโฟลเดอร์ "output" หากยังไม่มี
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ย้ายไฟล์ _output.jpg ไปยังโฟลเดอร์ "output"
for f in files:
    output_file = os.path.join(output_folder, os.path.basename(f.replace(".jpg", "_output.jpg")))
    shutil.move(f.replace(".jpg", "_output.jpg"), output_file)
