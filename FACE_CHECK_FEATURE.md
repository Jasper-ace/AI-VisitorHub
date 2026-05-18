# Face Duplicate Check Feature

## 🔍 **New Registration Face Check**

### **Feature Overview**
When a user clicks "Capture" during visitor registration, the system now automatically checks if the captured face already exists in the database before allowing registration to proceed.

### **🚀 How It Works**

#### **1. Capture Process**
1. User positions face in camera frame
2. Clicks "📸 Capture" button
3. System captures photo and shows "🔍 Checking..." status
4. Performs face recognition against existing database
5. Shows result based on findings

#### **2. Possible Outcomes**

**✅ New Face (Success)**
- Face not found in database
- Shows: "Face verified successfully! Please complete the registration form."
- Allows user to proceed with registration form
- Status: "✅ New face verified - fill in details and register."

**❌ Existing Face (Error)**
- Face matches existing visitor in database
- Shows: "This face is already registered as '[Name]'. Please use Face ID Check-In instead."
- Displays confidence percentage
- Provides link to Face ID Check-In page
- Clears captured photo and resets capture button

**⚠️ Detection Issues**
- No face detected or eyes not visible
- Shows appropriate error message
- Allows user to try capturing again

### **🔧 Technical Implementation**

#### **New API Endpoint**
```
POST /api/check_face
```
- Accepts base64 photo data
- Performs liveness detection (face + eyes)
- Runs face recognition against database
- Returns match status and visitor info if found

#### **Enhanced Registration Flow**
```javascript
1. Capture photo
2. Call /api/check_face
3. If face exists → Show error + redirect option
4. If face new → Allow registration
5. If detection fails → Show error + retry
```

### **🎨 User Experience**

#### **Visual Feedback**
- **Loading State**: Button shows "🔍 Checking..." during verification
- **Success State**: Green message with checkmark
- **Error State**: Red message with helpful guidance
- **Status Updates**: Real-time status text updates

#### **Error Handling**
- Clear error messages explaining the issue
- Automatic photo clearing on errors
- Reset button state for retry
- Helpful navigation links

### **🛡️ Security Benefits**

1. **Prevents Duplicate Registrations**: Same person can't register multiple times
2. **Database Integrity**: Maintains clean visitor records
3. **User Guidance**: Directs existing users to correct process
4. **Fraud Prevention**: Reduces potential for identity confusion

### **📱 User Journey**

#### **New Visitor**
1. Capture face → ✅ Verification success
2. Fill registration form → Submit
3. Successfully registered

#### **Existing Visitor**
1. Capture face → ❌ Face already registered
2. See error message with existing name
3. Click link to go to Face ID Check-In
4. Use existing registration for access

### **🔗 Integration Points**

- **Registration Page**: `/register` - Enhanced capture process
- **Check-In Page**: `/checkin` - Redirect destination for existing users
- **Database**: Queries existing visitor faces for matches
- **Face Recognition**: Uses same DeepFace engine as check-in system

### **⚡ Performance**
- Fast face recognition using existing DeepFace infrastructure
- Efficient database queries against visitor photos
- Minimal impact on registration flow
- Graceful fallback for demo mode

This feature ensures data integrity while providing a smooth user experience that guides visitors to the appropriate process based on their registration status.