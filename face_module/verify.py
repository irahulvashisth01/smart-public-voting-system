import cv2

def verify_face():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer/trainer.yml")

    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    matched_label = None
    lowest_confidence = 999

    for i in range(10):   # Try 10 frames instead of 1
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            label, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            print("Detected Label:", label)
            print("Confidence:", confidence)

            if confidence < lowest_confidence:
                lowest_confidence = confidence
                matched_label = label

    cam.release()
    cv2.destroyAllWindows()

    # Adjust threshold here
    if lowest_confidence < 80:
        return matched_label
    else:
        return None
