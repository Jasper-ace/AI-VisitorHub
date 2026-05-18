# Visitor Face ID System
## IAS2 Finals Project — DeepFace + Flask + Face ID Technology

---

## Project Overview
An advanced security system with iPhone-like Face ID technology that automatically detects faces and uses blink verification for anti-spoofing. No buttons needed - just look at the camera and blink!

## ✨ New Face ID Features
- 🔐 **Automatic Face Detection** - No capture button needed
- 👁️ **Real-time Eye Detection** - Ensures both eyes are visible
- 🔒 **Blink Verification** - Anti-spoofing protection like iPhone Face ID
- ⚡ **Instant Recognition** - Seamless user experience
- 🎯 **Dynamic Face Tracking** - Face box follows detected faces
- 🛡️ **Liveness Detection** - Prevents photo/video spoofing attacks

## Core Features
- 📷 **Live webcam face capture** for registration
- 🔍 **DeepFace-powered recognition** with confidence scoring (VGG-Face model)
- ✅ **Check-in / Check-out** tracking with timestamps
- 🚨 **Security alerts** for unrecognized faces
- 🔒 **Blacklist** management for blocked visitors
- 📊 **Admin dashboard** with real-time stats, logs, and visitor management
- 🗄️ **SQLite database** for persistent storage

---

## Setup Instructions

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```
> Note: DeepFace + TensorFlow may take a few minutes to install.

### 2. Run the application
```bash
python app.py
```

### 3. Access the system
| Page           | URL                             |
|----------------|---------------------------------|
| Home           | http://localhost:5000           |
| Register       | http://localhost:5000/register  |
| **Face ID Check-In** | http://localhost:5000/checkin   |
| Admin Login    | http://localhost:5000/admin/login |

### 4. Admin Credentials
| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

---

## 🔐 How Face ID Works

### 1. **Face Detection**
- System continuously scans for faces using OpenCV Haar Cascades
- Detects face position and draws dynamic tracking box
- Ensures face is properly positioned and sized

### 2. **Eye Detection & Liveness Check**
- Detects both eyes to ensure user is facing camera
- Verifies both eyes are open and visible
- Prevents spoofing with photos or videos

### 3. **Blink Verification**
- Prompts user to blink for anti-spoofing
- Simulates iPhone Face ID liveness detection
- Only proceeds after successful blink verification

### 4. **Face Recognition**
- Uses DeepFace AI to match against registered visitors
- Returns confidence score and visitor information
- Logs successful/failed attempts with timestamps

---

## Project Structure
```
visitor_system/
├── app.py                  # Main Flask application with Face ID APIs
├── requirements.txt        # Python dependencies
├── database/
│   └── visitors.db         # SQLite database (auto-created)
├── visitor_faces/          # Stored face photos (auto-created)
├── logs/                   # Log files (auto-created)
└── templates/
    ├── base.html           # Base layout with navigation
    ├── index.html          # Landing page with Face ID branding
    ├── register.html       # Visitor registration + webcam
    ├── checkin.html        # Face ID check-in/out (NEW!)
    ├── admin_login.html    # Admin login
    └── admin_dashboard.html # Full admin panel
```

---

## Face Recognition Details
| Setting     | Value         |
|-------------|---------------|
| Model       | VGG-Face      |
| Backend     | OpenCV        |
| Distance    | Cosine        |
| Threshold   | Auto (DeepFace default) |
| **Face Detection** | **Haar Cascades** |
| **Eye Detection** | **Haar Cascades** |
| **Anti-Spoofing** | **Blink Verification** |

You can change the model in `app.py`:
```python
RECOGNITION_MODEL   = "VGG-Face"   # or: Facenet, ArcFace, Dlib
RECOGNITION_BACKEND = "opencv"     # or: retinaface, mtcnn, ssd
RECOGNITION_DISTANCE = "cosine"    # or: euclidean, euclidean_l2
```

---

## API Endpoints
| Method | Endpoint                        | Description             |
|--------|---------------------------------|-------------------------|
| POST   | `/api/register`                 | Register a new visitor  |
| **POST** | **`/api/detect_face`**        | **Face & eye detection (NEW!)** |
| POST   | `/api/checkin`                  | Face ID recognition entry |
| GET    | `/api/stats`                    | Dashboard statistics    |
| GET    | `/api/visitors`                 | List all visitors       |
| GET    | `/api/logs`                     | Visit log history       |
| GET    | `/api/alerts`                   | Security alerts         |
| POST   | `/api/alerts/<id>/resolve`      | Resolve an alert        |
| POST   | `/api/visitors/<uuid>/status`   | Update visitor status   |

---

## Security Features
- 🛡️ **Anti-Spoofing**: Blink detection prevents photo attacks
- 👁️ **Liveness Detection**: Ensures real person, not video/image
- 🔒 **Eye Verification**: Both eyes must be visible and open
- 📊 **Confidence Scoring**: AI confidence levels for each match
- 🚨 **Alert System**: Automatic alerts for suspicious activity
- 📝 **Audit Trail**: Complete logging of all access attempts

---

## Group Members
*(Fill in your group names here)*

---

## Technologies Used
- **Flask** — Python web framework
- **DeepFace** — Facebook AI face recognition library
- **OpenCV** — Face/eye detection and image processing
- **SQLite** — Lightweight database
- **Vanilla JS** — WebRTC webcam capture, real-time face detection
- **CSS3** — Modern UI with Face ID animations
