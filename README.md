# WEB_CAM
A application that connect multiple cameras work like a CCTV system
# 📷 AI-Powered Multi-Camera Surveillance System

This project is an AI-powered multi-camera surveillance web application built using **Streamlit** and **Flask**. It supports real-time video feed from multiple IP cameras, object detection using **YOLO**, and role-based user management. Ideal for security monitoring, analysis, and smart surveillance.

---

## 🔧 Project Structure

├── .env # Environment variables (API keys, secrets)
├── README.md # Project documentation
├── app.py # Main entry point to run both Streamlit and Flask
├── flask_backend.py # Flask backend for camera feed, API handling
├── streamlit_frontend.py # Streamlit UI for live camera selection and dashboard
├── camera_manager.py # Handles connection to multiple IP cameras
├── yolo_detector.py # YOLOv8-based object detection logic
├── config.py # Global configuration settings
├── database.py # Database logic for storing logs, users, activity
├── requirements.txt # Python dependencies

---

## 🚀 Features

- 📸 Connect and manage multiple IP cameras
- 🤖 Real-time object detection with **YOLOv8**
- 🔐 User authentication with role-based access
- 📊 Live camera dashboard with Streamlit
- 🛠️ Easy configuration using `.env` and `config.py`
- 🗃️ Logging and database integration
- 📡 Flask REST APIs for backend communication

---

## 🖥️ Technologies Used

- **Python**
- **Streamlit**
- **Flask**
- **YOLOv8**
- **OpenCV**
- **PostgreSQL / SQLite**
- **dotenv**

---

## ⚙️ Setup Instructions

1. **Clone the repository**

git clone https://github.com/your-username/your-repo.git
cd your-repo
Create and activate a virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

pip install -r requirements.txt
Set environment variables

Create a .env file:

FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
CAMERA_1_URL=http://192.168.1.x:8080/video
CAMERA_2_URL=http://192.168.1.y:8080/video
Run the app

python app.py
📂 File Descriptions
.env: Sensitive configuration values.

README.md: Documentation file (you're reading it!).

app.py: Orchestrates both Streamlit frontend and Flask backend.

flask_backend.py: Handles REST API and video stream routing.

streamlit_frontend.py: Builds the interactive frontend dashboard.

camera_manager.py: Connects and manages multiple IP camera streams.

yolo_detector.py: Performs object detection using YOLOv8.

config.py: Central place for default settings and constants.

database.py: Manages user info, logs, and camera events.

requirements.txt: All required Python libraries and versions.

🧠 Future Enhancements
Add camera zone selection

Enable alert system for detections

Role-based dashboard analytics

Face recognition integration

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first.

