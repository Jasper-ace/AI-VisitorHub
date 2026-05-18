"""
Visitor Face Recognition System
IAS2 Finals Project - Flask + DeepFace
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import os
import base64
import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

# DeepFace imports (graceful fallback for demo)
try:
    from deepface import DeepFace
    import cv2
    import numpy as np
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[WARNING] DeepFace/OpenCV not installed. Running in DEMO mode.")

app = Flask(__name__)
app.secret_key = "vrs-ias2-secret-2024"

# ─────────────── CONFIG ───────────────
DB_PATH        = "database/visitors.db"
FACES_DIR      = "visitor_faces"
LOGS_DIR       = "logs"
ADMIN_USER     = "admin"
ADMIN_PASS     = "admin123"
ALLOWED_EXTS   = {"png", "jpg", "jpeg"}
RECOGNITION_MODEL    = "VGG-Face"   # Facenet, ArcFace, etc.
RECOGNITION_BACKEND  = "opencv"     # retinaface, mtcnn, etc.
RECOGNITION_DISTANCE = "cosine"
# ──────────────────────────────────────


# ─────────────── DATABASE ───────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("database", exist_ok=True)
    os.makedirs(FACES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS visitors (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid        TEXT UNIQUE NOT NULL,
        name        TEXT NOT NULL,
        email       TEXT,
        phone       TEXT,
        purpose     TEXT,
        company     TEXT,
        photo_path  TEXT,
        registered_at TEXT,
        status      TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS visit_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        visitor_uuid TEXT,
        visitor_name TEXT,
        action      TEXT,   -- 'check_in' | 'check_out' | 'denied'
        confidence  REAL,
        timestamp   TEXT,
        notes       TEXT
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        type        TEXT,
        message     TEXT,
        visitor_uuid TEXT,
        timestamp   TEXT,
        photo_path  TEXT,
        resolved    INTEGER DEFAULT 0
    );
    """)
    
    # Migration: Add photo_path column to alerts if it doesn't exist
    try:
        cur.execute("ALTER TABLE alerts ADD COLUMN photo_path TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

# ─────────────── AUTH ───────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ─────────────── HELPERS ───────────────
def save_base64_image(b64_str, filename):
    """Decode base64 image string and save to disk."""
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    img_bytes = base64.b64decode(b64_str)
    path = os.path.join(FACES_DIR, filename)
    with open(path, "wb") as f:
        f.write(img_bytes)
    return path

def log_visit(visitor_uuid, visitor_name, action, confidence=None, notes=""):
    conn = get_db()
    conn.execute(
        "INSERT INTO visit_logs (visitor_uuid, visitor_name, action, confidence, timestamp, notes) VALUES (?,?,?,?,?,?)",
        (visitor_uuid, visitor_name, action, confidence, datetime.now().isoformat(), notes)
    )
    conn.commit()
    conn.close()

def create_alert(alert_type, message, visitor_uuid=None, photo_path=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO alerts (type, message, visitor_uuid, timestamp, photo_path) VALUES (?,?,?,?,?)",
        (alert_type, message, visitor_uuid, datetime.now().isoformat(), photo_path)
    )
    conn.commit()
    conn.close()

def detect_face_and_eyes(captured_b64):
    """Detect face and eyes in the captured image for liveness detection."""
    if not DEEPFACE_AVAILABLE:
        return {"face_detected": False, "demo": True}
    
    try:
        # Save temp image
        temp_path = os.path.join(FACES_DIR, "_temp_detection.jpg")
        save_base64_image(captured_b64, "_temp_detection.jpg")
        
        # Load image with OpenCV
        img = cv2.imread(temp_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load face and eye cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            os.remove(temp_path)
            return {"face_detected": False, "eyes_detected": 0}
        
        # For the first detected face, count eyes
        (x, y, w, h) = faces[0]
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        os.remove(temp_path)
        return {
            "face_detected": True, 
            "eyes_detected": len(eyes),
            "face_area": int(w * h),  # Convert to Python int
            "face_position": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}  # Convert to Python ints
        }
        
    except Exception as e:
        return {"face_detected": False, "error": str(e)}

def get_visitor_current_status(visitor_uuid):
    """Get the current status of a visitor (checked_in, checked_out, or never_visited)."""
    conn = get_db()
    
    # Get the most recent log entry for this visitor
    recent_log = conn.execute(
        "SELECT action FROM visit_logs WHERE visitor_uuid = ? ORDER BY timestamp DESC LIMIT 1",
        (visitor_uuid,)
    ).fetchone()
    
    conn.close()
    
    if not recent_log:
        return "never_visited"
    
    last_action = recent_log["action"]
    
    if last_action == "check_in":
        return "checked_in"
    elif last_action == "check_out":
        return "checked_out"
    else:
        return "checked_out"  # Default to checked_out for other actions like "denied"

def recognize_face(captured_b64):
    """Match a captured face against all registered visitor photos (including blocked ones)."""
    if not DEEPFACE_AVAILABLE:
        # DEMO mode – return fake result
        return {"match": False, "demo": True, "message": "DeepFace not installed (demo mode)"}

    try:
        # Save temp image
        temp_path = os.path.join(FACES_DIR, "_temp_query.jpg")
        save_base64_image(captured_b64, "_temp_query.jpg")

        conn = get_db()
        # Check ALL visitors regardless of status (active, blocked, etc.)
        visitors = conn.execute("SELECT uuid, name, photo_path, status FROM visitors").fetchall()
        conn.close()

        best_match = None
        best_distance = float("inf")

        for v in visitors:
            if not v["photo_path"] or not os.path.exists(v["photo_path"]):
                continue
            try:
                result = DeepFace.verify(
                    img1_path=temp_path,
                    img2_path=v["photo_path"],
                    model_name=RECOGNITION_MODEL,
                    detector_backend=RECOGNITION_BACKEND,
                    distance_metric=RECOGNITION_DISTANCE,
                    enforce_detection=False
                )
                if result["verified"] and result["distance"] < best_distance:
                    best_distance = result["distance"]
                    best_match = dict(v)
                    best_match["distance"] = result["distance"]
                    best_match["confidence"] = round((1 - result["distance"]) * 100, 2)
            except Exception:
                continue

        os.remove(temp_path)
        if best_match:
            return {"match": True, "visitor": best_match}
        return {"match": False}

    except Exception as e:
        return {"match": False, "error": str(e)}


# ═══════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════

# ─── Serve static images ───
@app.route("/static/img/<filename>")
def serve_static_image(filename):
    """Serve static images like logo and background."""
    from flask import send_from_directory
    import os
    # Ensure the file exists and is safe
    safe_filename = os.path.basename(filename)
    return send_from_directory("img", safe_filename)

# ─── Serve visitor photos ───
@app.route("/visitor_faces/<filename>")
def serve_visitor_photo(filename):
    """Serve visitor face photos securely."""
    from flask import send_from_directory
    import os
    # Ensure the file exists and is safe
    safe_filename = os.path.basename(filename)
    return send_from_directory(FACES_DIR, safe_filename)

# ─── Serve unverified face photos ───
@app.route("/unverified_faces/<filename>")
def serve_unverified_photo(filename):
    """Serve unverified face photos securely for admin review."""
    from flask import send_from_directory
    import os
    # Ensure the file exists and is safe
    safe_filename = os.path.basename(filename)
    # Unverified photos are also stored in FACES_DIR
    return send_from_directory(FACES_DIR, safe_filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/checkin")
def checkin_page():
    return render_template("checkin.html")

# ─── API: Register visitor ───
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    phone   = data.get("phone", "").strip()
    purpose = data.get("purpose", "").strip()
    company = data.get("company", "").strip()
    photo   = data.get("photo")   # base64

    if not name or not photo:
        return jsonify({"success": False, "message": "Name and photo are required."}), 400

    vid = str(uuid.uuid4())
    filename = f"{vid}.jpg"
    try:
        photo_path = save_base64_image(photo, filename)
    except Exception as e:
        return jsonify({"success": False, "message": f"Image error: {e}"}), 500

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO visitors (uuid, name, email, phone, purpose, company, photo_path, registered_at) VALUES (?,?,?,?,?,?,?,?)",
            (vid, name, email, phone, purpose, company, photo_path, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Registration error."}), 500
    finally:
        conn.close()

    log_visit(vid, name, "registered")
    return jsonify({"success": True, "message": f"Visitor '{name}' registered successfully!", "uuid": vid})

# ─── API: Check if face exists during registration ───
@app.route("/api/check_face", methods=["POST"])
def api_check_face():
    """Check if a captured face already exists in the database during registration."""
    data = request.json
    photo = data.get("photo")
    
    if not photo:
        return jsonify({"success": False, "message": "No photo provided."}), 400
    
    # First check for liveness (face and eyes detection)
    detection_result = detect_face_and_eyes(photo)
    
    if detection_result.get("demo"):
        return jsonify({"success": False, "demo": True,
                        "message": "DeepFace not installed. Please install requirements.txt."})
    
    if not detection_result.get("face_detected"):
        return jsonify({"success": False, "message": "No face detected. Please position your face in the frame."})
    
    if detection_result.get("eyes_detected", 0) < 2:
        return jsonify({"success": False, "message": "Both eyes must be visible for security verification."})
    
    # Check if face already exists in database
    recognition_result = recognize_face(photo)
    
    if recognition_result.get("demo"):
        return jsonify({"success": False, "demo": True,
                        "message": "DeepFace not installed. Please install requirements.txt."})
    
    if recognition_result.get("match"):
        # Face already exists
        visitor = recognition_result["visitor"]
        
        # Check visitor status
        if visitor["status"] in ["blocked", "blacklisted"]:
            return jsonify({
                "success": False, 
                "face_exists": True,
                "blocked": True,
                "visitor": {
                    "name": visitor["name"],
                    "uuid": visitor["uuid"][:8] + "...",
                    "confidence": visitor["confidence"],
                    "status": visitor["status"]
                },
                "message": f"Access Denied: {visitor['name']} is {visitor['status']} from the system. Contact management for assistance."
            })
        else:
            return jsonify({
                "success": False, 
                "face_exists": True,
                "blocked": False,
                "visitor": {
                    "name": visitor["name"],
                    "uuid": visitor["uuid"][:8] + "...",
                    "confidence": visitor["confidence"],
                    "status": visitor["status"]
                },
                "message": f"This face is already registered as '{visitor['name']}'. Please use Face ID Check-In instead."
            })
    else:
        # Face is new, can proceed with registration
        return jsonify({
            "success": True,
            "face_exists": False,
            "message": "Face verified. You can proceed with registration.",
            "liveness_check": {
                "face_detected": detection_result.get("face_detected", False),
                "eyes_detected": detection_result.get("eyes_detected", 0),
                "face_area": detection_result.get("face_area", 0)
            }
        })
@app.route("/api/detect_face", methods=["POST"])
def api_detect_face():
    data = request.json
    photo = data.get("photo")
    
    if not photo:
        return jsonify({"success": False, "message": "No photo provided."}), 400
    
    result = detect_face_and_eyes(photo)
    
    if result.get("demo"):
        return jsonify({"success": False, "demo": True, 
                       "message": "DeepFace not installed. Please install requirements.txt."})
    
    return jsonify({
        "success": True,
        "face_detected": result.get("face_detected", False),
        "eyes_detected": result.get("eyes_detected", 0),
        "face_area": result.get("face_area", 0),
        "face_position": result.get("face_position", {}),
        "liveness_check": result.get("eyes_detected", 0) >= 2  # Both eyes should be visible
    })

# ─── API: Face recognition check-in ───
@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    data   = request.json
    photo  = data.get("photo")
    action = data.get("action", "check_in")   # check_in | check_out
    blink_verified = data.get("blink_verified", False)  # Anti-spoofing check

    if not photo:
        return jsonify({"success": False, "message": "No photo provided."}), 400

    # First check for liveness (face and eyes detection)
    detection_result = detect_face_and_eyes(photo)
    
    if detection_result.get("demo"):
        return jsonify({"success": False, "demo": True,
                        "message": "DeepFace not installed. Please install requirements.txt."})
    
    if not detection_result.get("face_detected"):
        return jsonify({"success": False, "message": "No face detected. Please position your face in the frame."})
    
    if detection_result.get("eyes_detected", 0) < 2:
        return jsonify({"success": False, "message": "Both eyes must be visible for security verification."})
    
    if not blink_verified:
        return jsonify({"success": False, "message": "Please blink to verify you are a real person.", "require_blink": True})

    # Proceed with face recognition
    result = recognize_face(photo)

    if result.get("demo"):
        return jsonify({"success": False, "demo": True,
                        "message": "DeepFace not installed. Please install requirements.txt."})

    if result.get("match"):
        v = result["visitor"]
        
        # Check if visitor is blocked or blacklisted
        if v["status"] in ["blocked", "blacklisted"]:
            log_visit(v["uuid"], v["name"], "denied", v["confidence"], f"Access denied - visitor {v['status']}")
            create_alert("blocked_access", f"{v['status'].title()} visitor {v['name']} attempted access", v["uuid"])
            return jsonify({
                "success": False,
                "blocked": True,
                "visitor": {
                    "uuid": v["uuid"],
                    "name": v["name"],
                    "confidence": v["confidence"],
                    "status": v["status"]
                },
                "message": f"Access Denied: {v['name']} is {v['status']} from the system. Contact management."
            })
        
        # Check visitor's current status for active visitors
        current_status = get_visitor_current_status(v["uuid"])
        
        # Validate the action based on current status
        if action == "check_in" and current_status == "checked_in":
            return jsonify({
                "success": False, 
                "message": f"Error: {v['name']} is already checked in. Please switch to Check Out mode to check out."
            })
        elif action == "check_out" and current_status == "checked_out":
            return jsonify({
                "success": False, 
                "message": f"Error: {v['name']} is already checked out. Please switch to Check In mode to check in."
            })
        elif action == "check_out" and current_status == "never_visited":
            return jsonify({
                "success": False, 
                "message": f"Error: {v['name']} has never checked in. Please switch to Check In mode first."
            })
        
        # Log the valid action
        log_visit(v["uuid"], v["name"], action, v["confidence"])
        
        # Create appropriate success message
        if action == "check_in":
            message = f"Welcome, {v['name']}! You have successfully checked in."
        else:  # check_out
            message = f"Goodbye, {v['name']}! You have successfully checked out. Have a great day!"
        
        return jsonify({
            "success": True,
            "visitor": {
                "uuid": v["uuid"],
                "name": v["name"],
                "confidence": v["confidence"]
            },
            "action": action,
            "current_status": current_status,
            "message": message
        })
    else:
        # Save the unverified face photo for admin review
        unverified_filename = f"unverified_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"
        unverified_path = save_base64_image(photo, unverified_filename)
        
        create_alert("unknown_face", "Unrecognized face attempted entry.", photo_path=unverified_path)
        log_visit(None, "Unknown", "denied")
        return jsonify({"success": False, "message": "Face not recognized. Access denied."})

# ─── API: Dashboard stats ───
@app.route("/api/stats")
@login_required
def api_stats():
    conn = get_db()
    total_visitors = conn.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
    today = datetime.now().date().isoformat()
    today_checkins = conn.execute(
        "SELECT COUNT(*) FROM visit_logs WHERE action='check_in' AND timestamp LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    active_visitors = conn.execute(
        """SELECT COUNT(DISTINCT visitor_uuid) FROM visit_logs
           WHERE action='check_in' AND visitor_uuid NOT IN
           (SELECT visitor_uuid FROM visit_logs WHERE action='check_out' AND timestamp LIKE ?)""",
        (f"{today}%",)
    ).fetchone()[0]
    unresolved_alerts = conn.execute("SELECT COUNT(*) FROM alerts WHERE resolved=0").fetchone()[0]
    conn.close()
    return jsonify({
        "total_visitors": total_visitors,
        "today_checkins": today_checkins,
        "active_visitors": active_visitors,
        "unresolved_alerts": unresolved_alerts
    })

# ─── API: Recent logs ───
@app.route("/api/logs")
@login_required
def api_logs():
    limit = request.args.get("limit", 50, type=int)
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM visit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─── API: All visitors ───
@app.route("/api/visitors")
@login_required
def api_visitors():
    conn = get_db()
    rows = conn.execute("SELECT * FROM visitors ORDER BY registered_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─── API: Alerts ───
@app.route("/api/alerts")
@login_required
def api_alerts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM alerts WHERE resolved=0 ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
@login_required
def resolve_alert(alert_id):
    conn = get_db()
    conn.execute("UPDATE alerts SET resolved=1 WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ─── API: Blacklist/delete visitor ───
@app.route("/api/visitors/<string:vid>/status", methods=["POST"])
@login_required
def update_visitor_status(vid):
    status = request.json.get("status", "active")
    conn = get_db()
    conn.execute("UPDATE visitors SET status=? WHERE uuid=?", (status, vid))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ═══════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials.")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

# ─── Test route for creating unverified face alert ───
@app.route("/test/create_unverified_alert")
@login_required
def test_create_unverified_alert():
    """Test route to create an unverified face alert with photo."""
    # Create a test alert with a fake photo path
    test_photo_path = "visitor_faces/40d9f366-7f81-45fa-93eb-b303aec178e3.jpg"  # Use existing photo for test
    create_alert("unknown_face", "Test unverified face alert", photo_path=test_photo_path)
    return jsonify({"success": True, "message": "Test alert created"})


if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  Visitor Recognition System - IAS2 Finals")
    print(f"  DeepFace: {'Available' if DEEPFACE_AVAILABLE else 'NOT installed (demo mode)'}")
    print("  Admin: http://127.0.0.1:5000/admin/login")
    print("  Default credentials: admin / admin123")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
