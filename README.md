# 👶 ChildFinder – AI-Based Missing Child Identification System

**ChildFinder** is an AI-driven web application designed to assist in identifying and reuniting missing children using facial recognition technology. It includes user and police portals, secure image uploads, and admin oversight—built with a strong focus on real-world social impact.

---

## ✨ Features

### 👨‍👩‍👧 Public Portal
- Upload images of found children
- Submit missing child reports
- OTP-based verification during registration
- Track submission status

### 👮 Police/Admin Portal
- Admin login with access control
- Add and manage missing child records
- Auto-match submitted photos using AI (FaceNet + MTCNN)
- Manual match verification
- MongoDB for persistent storage

---

## 🔧 Tech Stack

- **Frontend:** HTML, CSS, JS (Vanilla or React)
- **Backend:** Flask (Python)
- **Database:** MongoDB
- **AI/ML:** MTCNN + FaceNet/ArcFace for face recognition
- **Security:** Email OTP, Role-based access

---

## 🚀 Getting Started

```bash
git clone https://github.com/Obleshb/ChildFinder.git
cd ChildFinder
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
