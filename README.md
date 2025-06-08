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

![Image](https://github.com/user-attachments/assets/9ddd52f4-b8ec-45e1-89dd-cb38e3b3373b)
![Image](https://github.com/user-attachments/assets/72c95785-8443-4fdf-a7a3-9811af62dc8c)
![Image](https://github.com/user-attachments/assets/1c2923db-c41d-4c8d-b571-a7bb002037dc)
![Image](https://github.com/user-attachments/assets/16e8d580-d2d7-40e1-a93a-5de5f60b260a)
