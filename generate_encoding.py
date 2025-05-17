# generate_encoding.py
import face_recognition as fr
import os
import pickle

# Folder with registered faces
db_path = "your_database_path"  # Replace with your actual path
faces = os.listdir(db_path)
known_face_encodings = []

print("Encoding started...")

for idx, face_file in enumerate(faces, start=1):
    image_path = os.path.join(db_path, face_file)
    image = fr.load_image_file(image_path)
    encoding = fr.face_encodings(image)
    if encoding:
        known_face_encodings.append(encoding[0])
        print(f"[{idx}/{len(faces)}] Encoded: {face_file}")
    else:
        print(f"[{idx}/{len(faces)}] No face detected in: {face_file}")

# Save the encodings
with open("encode.pickle", "wb") as f:
    pickle.dump(known_face_encodings, f)

print("Encoding completed. Saved to encode.pickle")
