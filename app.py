from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trainmate-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainmate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Models ───────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='member')
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    goal = db.Column(db.String(50), default='general')
    membership_plan = db.Column(db.String(50), default='basic')
    membership_expiry = db.Column(db.Date)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    joined_on = db.Column(db.Date, default=date.today)
    workouts = db.relationship('Workout', backref='user', lazy=True)
    progress_logs = db.relationship('Progress', backref='user', lazy=True)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    muscle_group = db.Column(db.String(50))
    exercise = db.Column(db.String(100))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight_kg = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    body_weight = db.Column(db.Float)
    body_fat = db.Column(db.Float, nullable=True)
    calories_consumed = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)

class MembershipPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float)
    duration_days = db.Column(db.Integer)
    features = db.Column(db.Text)

# ── DB INIT (FIXED POSITION) ────────────────────────────────────────────────

with app.app_context():
    db.create_all()

    # Create default admin
    if not User.query.filter_by(email='admin@trainmate.com').first():
        admin = User(
            name='Admin',
            email='admin@trainmate.com',
            password=generate_password_hash('admin123'),
            role='admin',
            membership_expiry=date(2099, 12, 31)
        )
        db.session.add(admin)
        db.session.commit()

# ── Helpers ──────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        u = User.query.get(session['user_id'])
        if not u or u.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def calc_bmi(weight, height):
    if weight and height:
        return round(weight / ((height / 100) ** 2), 1)
    return None

def bmi_category(b):
    if b is None: return 'N/A'
    if b < 18.5: return 'Underweight'
    if b < 25.0: return 'Normal'
    if b < 30.0: return 'Overweight'
    return 'Obese'


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name   = request.form['name']
        email  = request.form['email']
        pwd    = request.form['password']
        age    = request.form.get('age',    type=int)
        height = request.form.get('height', type=float)
        weight = request.form.get('weight', type=float)
        goal   = request.form.get('goal', 'general')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup'))

        user = User(
            name=name, email=email,
            password=generate_password_hash(pwd),
            age=age, height=height, weight=weight,
            goal=goal,
            membership_expiry=date.today() + timedelta(days=30)
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd   = request.form['password']
        user  = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, pwd):
            session['user_id']   = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}! 💪', 'success')
            return redirect(url_for('admin_dashboard') if user.role == 'admin' else url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out. See you at the next session!', 'info')
    return redirect(url_for('index'))

# ── Member ────────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    recent_workouts = (Workout.query
                       .filter_by(user_id=user.id)
                       .order_by(Workout.date.desc())
                       .limit(5).all())

    # Weight chart – last 30 days
    since = date.today() - timedelta(days=30)
    prog  = (Progress.query
             .filter(Progress.user_id == user.id, Progress.date >= since)
             .order_by(Progress.date).all())

    chart_labels  = [p.date.strftime('%b %d') for p in prog]
    chart_weights = [p.body_weight for p in prog]

    # Muscle group breakdown
    muscle_counts = {}
    for w in Workout.query.filter_by(user_id=user.id).all():
        muscle_counts[w.muscle_group] = muscle_counts.get(w.muscle_group, 0) + 1

    b = calc_bmi(user.weight, user.height)

    return render_template('dashboard.html',
        user=user,
        recent_workouts=recent_workouts,
        bmi_value=b,
        bmi_cat=bmi_category(b),
        chart_labels=json.dumps(chart_labels),
        chart_weights=json.dumps(chart_weights),
        muscle_counts=json.dumps(muscle_counts),
        today=date.today()
    )

@app.route('/workout', methods=['GET', 'POST'])
@login_required
def workout():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        w = Workout(
            user_id      = user.id,
            date         = datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            muscle_group = request.form['muscle_group'],
            exercise     = request.form['exercise'],
            sets         = request.form.get('sets',      type=int),
            reps         = request.form.get('reps',      type=int),
            weight_kg    = request.form.get('weight_kg', type=float),
            notes        = request.form.get('notes', '')
        )
        db.session.add(w)
        db.session.commit()
        flash('Workout logged! 🔥', 'success')
        return redirect(url_for('workout'))

    all_workouts = (Workout.query
                    .filter_by(user_id=user.id)
                    .order_by(Workout.date.desc()).all())
    return render_template('workout.html', workouts=all_workouts, today=date.today().isoformat())

@app.route('/workout/delete/<int:wid>')
@login_required
def delete_workout(wid):
    w = Workout.query.get_or_404(wid)
    if w.user_id != session['user_id']:
        flash('Not authorised.', 'danger')
        return redirect(url_for('workout'))
    db.session.delete(w)
    db.session.commit()
    flash('Workout entry removed.', 'info')
    return redirect(url_for('workout'))

@app.route('/progress', methods=['GET', 'POST'])
@login_required
def progress():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        p = Progress(
            user_id           = user.id,
            date              = datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            body_weight       = request.form.get('body_weight',       type=float),
            body_fat          = request.form.get('body_fat',          type=float),
            calories_consumed = request.form.get('calories_consumed', type=int),
            notes             = request.form.get('notes', '')
        )
        db.session.add(p)
        db.session.commit()
        # Update user's current weight
        if p.body_weight:
            user.weight = p.body_weight
            db.session.commit()
        flash('Progress saved! 📈', 'success')
        return redirect(url_for('progress'))

    logs = (Progress.query
            .filter_by(user_id=user.id)
            .order_by(Progress.date.desc()).all())

    # Full chart data
    all_prog = (Progress.query
                .filter_by(user_id=user.id)
                .order_by(Progress.date).all())
    chart_labels  = [p.date.strftime('%b %d') for p in all_prog]
    chart_weights = [p.body_weight   for p in all_prog]
    chart_cals    = [p.calories_consumed or 0 for p in all_prog]

    return render_template('progress.html',
        logs=logs,
        chart_labels=json.dumps(chart_labels),
        chart_weights=json.dumps(chart_weights),
        chart_cals=json.dumps(chart_cals),
        today=date.today().isoformat()
    )

@app.route('/diet')
@login_required
def diet():
    user = User.query.get(session['user_id'])
    return render_template('diet.html', user=user)

@app.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi_calc():
    result = None
    if request.method == 'POST':
        w = request.form.get('weight', type=float)
        h = request.form.get('height', type=float)
        b = calc_bmi(w, h)
        result = {'bmi': b, 'category': bmi_category(b), 'weight': w, 'height': h}
    return render_template('bmi.html', result=result)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name   = request.form['name']
        user.age    = request.form.get('age',    type=int)
        user.height = request.form.get('height', type=float)
        user.weight = request.form.get('weight', type=float)
        user.goal   = request.form.get('goal', 'general')
        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_members  = User.query.filter_by(role='member').count()
    total_trainers = User.query.filter_by(role='trainer').count()
    total_workouts = Workout.query.count()
    recent_members = (User.query
                      .filter_by(role='member')
                      .order_by(User.joined_on.desc())
                      .limit(8).all())
    expiring = (User.query
                .filter(User.membership_expiry <= date.today() + timedelta(days=7),
                        User.membership_expiry >= date.today()).all())
    return render_template('admin/dashboard.html',
        total_members=total_members,
        total_trainers=total_trainers,
        total_workouts=total_workouts,
        recent_members=recent_members,
        expiring=expiring
    )

@app.route('/admin/members')
@admin_required
def admin_members():
    members = User.query.filter(User.role != 'admin').order_by(User.joined_on.desc()).all()
    trainers = User.query.filter_by(role='trainer').all()
    return render_template('admin/members.html', members=members, trainers=trainers)

@app.route('/admin/member/add', methods=['GET', 'POST'])
@admin_required
def admin_add_member():
    if request.method == 'POST':
        plan     = request.form.get('plan', 'basic')
        days_map = {'basic': 30, 'standard': 90, 'premium': 365}
        expiry   = date.today() + timedelta(days=days_map.get(plan, 30))
        user = User(
            name             = request.form['name'],
            email            = request.form['email'],
            password         = generate_password_hash(request.form['password']),
            role             = request.form.get('role', 'member'),
            age              = request.form.get('age',    type=int),
            height           = request.form.get('height', type=float),
            weight           = request.form.get('weight', type=float),
            goal             = request.form.get('goal', 'general'),
            membership_plan  = plan,
            membership_expiry= expiry,
            trainer_id       = request.form.get('trainer_id', type=int) or None
        )
        if User.query.filter_by(email=user.email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin_add_member'))
        db.session.add(user)
        db.session.commit()
        flash(f'Member {user.name} added!', 'success')
        return redirect(url_for('admin_members'))
    trainers = User.query.filter_by(role='trainer').all()
    return render_template('admin/add_member.html', trainers=trainers)

@app.route('/admin/member/delete/<int:uid>')
@admin_required
def admin_delete_member(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    flash('Member removed.', 'info')
    return redirect(url_for('admin_members'))

@app.route('/admin/member/assign-trainer/<int:uid>', methods=['POST'])
@admin_required
def assign_trainer(uid):
    user = User.query.get_or_404(uid)
    user.trainer_id = request.form.get('trainer_id', type=int) or None
    db.session.commit()
    flash('Trainer assigned.', 'success')
    return redirect(url_for('admin_members'))

@app.route('/admin/plans')
@admin_required
def admin_plans():
    plans = MembershipPlan.query.all()
    return render_template('admin/plans.html', plans=plans)

@app.route('/admin/plans/add', methods=['POST'])
@admin_required
def admin_add_plan():
    features = [f.strip() for f in request.form.get('features','').split('\n') if f.strip()]
    plan = MembershipPlan(
        name          = request.form['name'],
        price         = request.form.get('price', type=float),
        duration_days = request.form.get('duration_days', type=int),
        features      = json.dumps(features)
    )
    db.session.add(plan)
    db.session.commit()
    flash('Plan added!', 'success')
    return redirect(url_for('admin_plans'))

# ── API (JSON) ────────────────────────────────────────────────────────────────

@app.route('/api/workout-suggestions')
@login_required
def workout_suggestions():
    user = User.query.get(session['user_id'])
    suggestions = {
        'bulk': {
            'Chest':     ['Bench Press 4x8','Incline Dumbbell Press 4x10','Cable Flyes 3x12','Push-ups 3xfailure'],
            'Back':      ['Deadlift 4x5','Pull-ups 4x8','Barbell Row 4x8','Lat Pulldown 3x12'],
            'Legs':      ['Squat 4x8','Romanian Deadlift 4x10','Leg Press 4x12','Calf Raises 4x15'],
            'Shoulders': ['Overhead Press 4x8','Lateral Raises 4x12','Face Pulls 3x15'],
            'Arms':      ['Barbell Curl 4x10','Tricep Dips 4x12','Hammer Curls 3x12','Skull Crushers 3x10'],
        },
        'cut': {
            'Chest':     ['Push-ups 4x20','Dumbbell Flyes 4x15','Cable Crossover 4x15'],
            'Back':      ['Pull-ups 4x10','Seated Cable Row 4x15','Dumbbell Row 4x12'],
            'Legs':      ['Lunges 4x15','Step-ups 4x15','Leg Curl 4x15','Jump Squats 3x20'],
            'Shoulders': ['Arnold Press 4x12','Band Pull-apart 4x20','Upright Row 3x15'],
            'Arms':      ['EZ Curl 4x12','Tricep Pushdown 4x15','Concentration Curl 3x15'],
        },
        'general': {
            'Chest':     ['Bench Press 3x10','Push-ups 3x15','Cable Flyes 3x12'],
            'Back':      ['Pull-ups 3x8','Barbell Row 3x10','Lat Pulldown 3x12'],
            'Legs':      ['Squat 3x10','Leg Press 3x12','Lunges 3x12'],
            'Shoulders': ['Overhead Press 3x10','Lateral Raises 3x12'],
            'Arms':      ['Bicep Curl 3x12','Tricep Pushdown 3x12'],
        }
    }
    goal = user.goal if user.goal in suggestions else 'general'
    return jsonify(suggestions[goal])

# ── Init ──────────────────────────────────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin
        if not User.query.filter_by(email='admin@trainmate.com').first():
            admin = User(
                name='Admin',
                email='admin@trainmate.com',
                password=generate_password_hash('admin123'),
                role='admin',
                membership_expiry=date(2099, 12, 31)
            )
            db.session.add(admin)

        # Seed membership plans
        if not MembershipPlan.query.first():
            plans = [
                MembershipPlan(name='Basic',    price=499,  duration_days=30,
                               features=json.dumps(['Gym Access','Locker Room'])),
                MembershipPlan(name='Standard', price=1199, duration_days=90,
                               features=json.dumps(['Gym Access','Locker Room','1 PT Session/month','Diet Consultation'])),
                MembershipPlan(name='Premium',  price=3999, duration_days=365,
                               features=json.dumps(['Unlimited Access','Personal Trainer','Diet Plan','Body Composition Analysis','Sauna'])),
            ]
            db.session.add_all(plans)

        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
