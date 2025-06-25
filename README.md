# FaceAuth: Local Face Authentication for File Security

**Fast, local face authentication system using Python, OpenCV, and modern deep learning.  
Secure, private, and easy-to-integrate file encryption with your face as the key.**

---

## 🚀 Overview

FaceAuth enables local, privacy-respecting face authentication to lock and unlock your sensitive files.  
No cloud, no third parties: everything stays **on your machine**.

- Modern deep learning (face embedding)
- Robust, fast authentication
- Encrypt/decrypt any file
- CLI-first, simple integration

---

## ⚡️ MVP Features

- Face registration (enrollment) via webcam
- Fast face authentication (real-time verification)
- Encrypt files with face authentication
- Decrypt files with face authentication
- All operations via a single CLI tool
- All face data stored locally and securely

> See [roadmap.md](roadmap.md) for details and upcoming features.

---

## 🛠️ Installation

> Requirements: Python 3.8+, OpenCV, numpy, and a modern face recognition model (e.g. InsightFace, FaceNet, ArcFace).

```bash
git clone https://github.com/yourusername/faceauth.git
cd faceauth
pip install -r requirements.txt
