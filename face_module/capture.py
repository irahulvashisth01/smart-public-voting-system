import cv2
import os

def capture_images(user_id):
    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = 0
    os.makedirs(f"dataset/user_{user_id}", exist_ok=True)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            cv2.imwrite(f"dataset/user_{user_id}/{count}.jpg",
                        gray[y:y+h, x:x+w])
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)

        cv2.imshow("Capturing Face", img)

        if count >= 40:   # Capture 40 images
            break

    cam.release()
    cv2.destroyAllWindows()
