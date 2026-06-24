import os
import cv2

input_path = "frames/train"
output_path = "faces/train"

classes = ["real", "fake"]

# load face detector
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

for c in classes:
    input_folder = os.path.join(input_path, c)
    output_folder = os.path.join(output_path, c)

    os.makedirs(output_folder, exist_ok=True)

    for img_name in os.listdir(input_folder):

        img_path = os.path.join(input_folder, img_name)
        img = cv2.imread(img_path)

        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # if face found
        for (x, y, w, h) in faces:

            face = img[y:y+h, x:x+w]

            if face.size == 0:
                continue

            face = cv2.resize(face, (224, 224))

            save_path = os.path.join(output_folder, img_name)
            cv2.imwrite(save_path, face)

            break   # take only first face

    print(f"Done: {c}")

print("Face extraction completed!")