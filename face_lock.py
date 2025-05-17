# face_lock.py
import face_recognition as fr
import pickle
import cv2

# Camera Opening
video_capture = cv2.VideoCapture(0)

# Load known face encodings
with open("encode.pickle", "rb") as f:
    known_face_encodings = pickle.load(f)

print("Face Lock Active. Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to read from camera.")
        break

    # Face detection and coding
    face_locations = fr.face_locations(frame, model="hog")
    face_encodings = fr.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        matches = fr.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)

        if True in matches:
            print("✅ Welcome!")
        else:
            print("❌ Access Denied")

    # Press q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()