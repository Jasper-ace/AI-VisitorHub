# Avida Residence New Manila VisitorsHub
## Advanced Face Recognition Visitor Management System

---

## Project Overview
An advanced security system with iPhone-like Face ID technology that automatically detects faces and uses blink verification for anti-spoofing. Designed specifically for **Avida Residence New Manila** with professional lobby-style interface and silent operation.

## ✨ Key Features
- 🔐 **Automatic Face Detection** - No capture button needed
- 👁️ **Real-time Eye Detection** - Ensures both eyes are visible
- 🔒 **Blink Verification** - Anti-spoofing protection like iPhone Face ID
- ⚡ **Instant Recognition** - Seamless user experience
- 🛡️ **Person Presence Detection** - Prevents multiple attempts by same person
- ⏱️ **3-Second Cooldown** - Professional timing controls
- � **Silent Operation** - Visual feedback only
- 🏢 **Condominium Branding** - Avida Residence New Manila themed

---

## 🚀 Quick Setup (Clone to Other Device)

### Prerequisites
- **Python 3.8+** installed
- **Git** installed
- **Webcam/Camera** access
- **Windows/Mac/Linux** compatible

### Step 1: Clone the Repository
```bash
# Clone from your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/avida-visitors-hub.git

# Or if using a different Git service:
git clone https://gitlab.com/yourusername/avida-visitors-hub.git

# Navigate to project directory
cd avida-visitors-hub
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```
> ⚠️ **Note**: DeepFace + TensorFlow installation may take 5-10 minutes and requires ~2GB download.

### Step 4: Run the Application
```bash
# Start the Flask server
python app.py
```

### Step 5: Access the System
| Page | URL | Description |
|------|-----|-------------|
| **Home** | http://localhost:5000 | Main landing page |
| **Registration** | http://localhost:5000/register | Register new visitors |
| **Check-In/Out** | http://localhost:5000/checkin | Face ID recognition |
| **Admin Panel** | http://localhost:5000/admin/login | Management dashboard |

### Step 6: Admin Access
| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |

---

## 🌐 Network Setup (Access from Other Devices)

### Local Network Access
To access from other devices on the same network:

1. **Find your IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. **Update Flask configuration** in `app.py`:
   ```python
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=5000, debug=True)
   ```

3. **Access from other devices:**
   ```
   http://YOUR_IP_ADDRESS:5000
   # Example: http://192.168.1.100:5000
   ```

### Firewall Configuration
- **Windows**: Allow Python through Windows Firewall
- **Mac**: System Preferences → Security & Privacy → Firewall
- **Linux**: Configure iptables or ufw as needed

---

## 📁 Project Structure
```
avida-visitors-hub/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/
│   └── visitors.db         # SQLite database (auto-created)
├── visitor_faces/          # Stored visitor photos (auto-created)
├── logs/                   # System logs (auto-created)
├── img/                    # Avida branding assets
│   ├── logo.png           # Avida Residence logo
│   └── bg.png             # Background image
└── templates/
    ├── base.html           # Base layout template
    ├── index.html          # Landing page
    ├── register.html       # Visitor registration
    ├── checkin.html        # Face ID check-in/out
    ├── admin_login.html    # Admin login
    └── admin_dashboard.html # Admin management panel
```

---

## 🔧 Configuration Options

### Camera Settings
In `app.py`, adjust camera resolution:
```python
# Default: 640x480
video: {width: 640, height: 480}

# HD: 1280x720
video: {width: 1280, height: 720}
```

### Face Recognition Model
```python
RECOGNITION_MODEL = "VGG-Face"      # Options: VGG-Face, Facenet, ArcFace
RECOGNITION_BACKEND = "opencv"      # Options: opencv, retinaface, mtcnn
RECOGNITION_DISTANCE = "cosine"     # Options: cosine, euclidean
```

### Person Presence Detection
In `templates/checkin.html`:
```javascript
const PERSON_LEFT_THRESHOLD = 5;   // Frames before considering person left
```

---

## 🔐 Security Features

### Anti-Spoofing Protection
- **Blink Detection**: Requires natural blinking
- **Eye Verification**: Both eyes must be visible
- **Liveness Check**: Prevents photo/video attacks
- **Person Presence**: Blocks rapid successive attempts

### Access Control
- **Visitor Status**: Active, Blocked, Blacklisted
- **Confidence Scoring**: AI confidence levels
- **Audit Trail**: Complete access logging
- **Security Alerts**: Unrecognized face notifications

---

## 🚨 Troubleshooting

### Camera Not Working
1. **Check browser permissions** - Allow camera access
2. **Try different browser** - Chrome/Firefox recommended
3. **Check camera drivers** - Ensure webcam is functional
4. **Restart application** - `Ctrl+C` then `python app.py`

### DeepFace Installation Issues
```bash
# If TensorFlow fails to install:
pip install --upgrade pip
pip install tensorflow==2.13.0
pip install deepface

# For M1 Macs:
pip install tensorflow-macos
pip install tensorflow-metal
```

### Network Access Issues
1. **Check firewall settings**
2. **Verify IP address** - Use `ipconfig`/`ifconfig`
3. **Test local access first** - http://localhost:5000
4. **Check port availability** - Port 5000 should be free

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm database/visitors.db
python app.py  # Will recreate database
```

---

## 📱 Mobile Device Access

The system is responsive and works on mobile devices:
- **Tablets**: Full functionality with touch interface
- **Smartphones**: Optimized for mobile cameras
- **iOS/Android**: Compatible with mobile browsers

---

## 🔄 Updates and Maintenance

### Updating the System
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python app.py
```

### Backup Important Data
```bash
# Backup database
cp database/visitors.db database/visitors_backup.db

# Backup visitor photos
cp -r visitor_faces visitor_faces_backup
```

---

## 🏢 Avida Residence New Manila Branding

This system is specifically customized for:
- **Avida Residence New Manila VisitorsHub**
- Professional condominium lobby interface
- Silent operation (no voice announcements)
- Corporate red accent color scheme (#e53e3e)
- Residential-focused visitor management

---

## � Support

For technical support or questions:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify camera and network permissions

---

## 🛠️ Technologies Used
- **Flask** — Python web framework
- **DeepFace** — Facebook AI face recognition
- **OpenCV** — Computer vision and face detection
- **SQLite** — Lightweight database
- **JavaScript** — WebRTC camera access and UI
- **CSS3** — Modern responsive design

---

## 📄 License
This project is developed for Avida Residence New Manila visitor management purposes.
