import cv2
import os
import numpy as np

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []

    for user_folder in os.listdir("dataset"):
        label = int(user_folder.split("_")[1])

        for image in os.listdir(f"dataset/{user_folder}"):
            img_path = f"dataset/{user_folder}/{image}"
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            faces.append(img)
            labels.append(label)

    recognizer.train(faces, np.array(labels))
    recognizer.save("trainer/trainer.yml")
