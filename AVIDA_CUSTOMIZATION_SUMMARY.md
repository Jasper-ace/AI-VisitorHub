# Avida Towers New Manila - Visitor Management System

## 🏢 Customization Summary

### **Branding Updates**

#### **1. Logo & Background Integration**
- ✅ Added logo serving route: `/static/img/<filename>`
- ✅ Updated navigation with Avida Towers New Manila logo
- ✅ Integrated background image across all pages
- ✅ Updated color scheme from green to blue theme

#### **2. Page Titles & Content**
- ✅ **Home Page**: "Avida Towers New Manila" with condominium-specific content
- ✅ **Registration**: Updated for condominium visitor registration
- ✅ **Check-in**: "Visitor Check-In" with Avida branding
- ✅ **Admin Dashboard**: "Avida Towers New Manila - Visitor Management Dashboard"
- ✅ **Admin Login**: Condominium management login with logo

#### **3. Purpose of Visit Enhancement**
- ✅ **Condominium-specific purposes**:
  - Visiting Resident
  - Delivery / Courier
  - Maintenance / Repair
  - Real Estate Viewing
  - Business Meeting
  - Service Provider
  - Guest / Family Visit
  - Others (with custom text input)

#### **4. "Others" Purpose Functionality**
- ✅ **Dynamic text box**: Appears when "Others" is selected
- ✅ **Validation**: Requires specification when "Others" is chosen
- ✅ **Data format**: Saves as "Others: [custom text]"
- ✅ **Form reset**: Clears custom text when different purpose selected

### **Technical Implementation**

#### **Files Modified:**
1. **`app.py`** - Added static image serving route
2. **`templates/base.html`** - Logo, background, blue theme
3. **`templates/index.html`** - Condominium homepage content
4. **`templates/register.html`** - Purpose options + Others functionality
5. **`templates/checkin.html`** - Updated branding
6. **`templates/admin_dashboard.html`** - Admin panel branding
7. **`templates/admin_login.html`** - Login page with logo

#### **Assets:**
- **Logo**: `img/logo.png` → served via `/static/img/logo.png`
- **Background**: `img/bg.png` → served via `/static/img/bg.png`

### **Color Scheme Changes**
```css
/* Old (Green Theme) */
--accent: #00e5a0;

/* New (Blue Theme) */
--accent: #0077ff;
--accent2: #00a8ff;
```

### **Purpose Options (Condominium-Specific)**
1. Visiting Resident
2. Delivery / Courier  
3. Maintenance / Repair
4. Real Estate Viewing
5. Business Meeting
6. Service Provider
7. Guest / Family Visit
8. **Others** (with custom input field)

### **JavaScript Enhancement**
```javascript
// Auto-show/hide custom purpose input
document.getElementById('f-purpose').addEventListener('change', function() {
    const otherGroup = document.getElementById('other-purpose-group');
    if (this.value === 'Others') {
        otherGroup.style.display = 'block';
        document.getElementById('f-other-purpose').focus();
    } else {
        otherGroup.style.display = 'none';
        document.getElementById('f-other-purpose').value = '';
    }
});
```

### **Testing**
- ✅ Flask application running successfully
- ✅ Images served correctly via new route
- ✅ All pages display Avida branding
- ✅ "Others" purpose functionality working
- ✅ Form validation includes custom purpose text

### **Access URLs**
- **Homepage**: http://127.0.0.1:5000/
- **Registration**: http://127.0.0.1:5000/register
- **Check-in**: http://127.0.0.1:5000/checkin
- **Admin**: http://127.0.0.1:5000/admin/login
- **Test Page**: http://127.0.0.1:5000/test_others_purpose.html

### **Admin Credentials**
- **Username**: admin
- **Password**: admin123

---

## 🎯 **Completed Features**

✅ **Condominium Branding**: Full Avida Towers New Manila integration  
✅ **Logo Integration**: Professional logo display across all pages  
✅ **Background Design**: Branded background image implementation  
✅ **Purpose Enhancement**: Condominium-specific visit purposes  
✅ **Others Functionality**: Dynamic custom purpose input field  
✅ **Color Theme**: Professional blue color scheme  
✅ **Admin Interface**: Branded management dashboard  

The visitor management system is now fully customized for Avida Towers New Manila condominium with professional branding and enhanced functionality.