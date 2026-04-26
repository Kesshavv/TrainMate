# ⚡ TrainMate — Gym Management System

> A full-stack gym management web app built with **Flask + SQLite**. Track workouts, monitor progress, follow diet plans, calculate BMI, and manage gym members — all from a sleek dark dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🚀 Features

### 👤 Member Side
- ✅ Signup / Login with hashed passwords
- ✅ Workout logger (muscle group, sets, reps, weight)
- ✅ AI-style workout suggestions based on your goal (bulk / cut / general)
- ✅ Progress tracker — weight, body fat %, calories
- ✅ Beautiful charts (weight over time, muscle group breakdown)
- ✅ Personalized diet plans (Bulking / Cutting / Maintenance)
- ✅ BMI Calculator with health category
- ✅ Profile management

### 🛡️ Admin Side
- ✅ Admin dashboard with member stats
- ✅ Add / remove members
- ✅ Assign trainers to members
- ✅ Manage membership plans (Basic / Standard / Premium)
- ✅ Expiring membership alerts

---

## 🛠️ Tech Stack

| Layer      | Tech                        |
|------------|-----------------------------|
| Backend    | Python 3.10+, Flask 3.0     |
| Database   | SQLite via Flask-SQLAlchemy |
| Frontend   | HTML5, CSS3, Vanilla JS     |
| Charts     | Chart.js                    |
| Auth       | Werkzeug password hashing   |

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Kesshavv/trainmate.git
cd trainmate
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🔑 Default Admin Credentials

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@trainmate.com    |
| Password | admin123               |

> ⚠️ Change the admin password in production!

---

## 📁 Project Structure

```
trainmate/
├── app.py                  # Flask routes & models
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
├── instance/
│   └── trainmate.db        # SQLite DB (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Full dark theme design
│   └── js/
│       └── main.js         # UI interactions
└── templates/
    ├── base.html           # Base layout + GitHub badge
    ├── index.html          # Landing page
    ├── login.html
    ├── signup.html
    ├── dashboard.html      # Member dashboard + charts
    ├── workout.html        # Workout logger
    ├── progress.html       # Progress tracker + charts
    ├── diet.html           # Diet plans (Bulk/Cut/Maintain)
    ├── bmi.html            # BMI calculator
    ├── profile.html        # User profile
    └── admin/
        ├── dashboard.html
        ├── members.html
        ├── add_member.html
        └── plans.html
```

---

## 📸 Pages Overview

| Page | Description |
|------|-------------|
| `/` | Landing page with features & pricing |
| `/dashboard` | Member dashboard with charts |
| `/workout` | Log & view workouts |
| `/progress` | Track weight, calories, body fat |
| `/diet` | Bulking / Cutting / Maintenance meal plans |
| `/bmi` | BMI calculator |
| `/profile` | Edit your profile |
| `/admin` | Admin panel |

---

## 🤝 Contributing

Pull requests are welcome! Feel free to fork and improve TrainMate.

---

## 👤 Author

**Kesshavv**  
GitHub: [@Kesshavv](https://github.com/Kesshavv)

---

## 📄 License

MIT License — free to use and modify.
