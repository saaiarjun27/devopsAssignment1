"""
ACEest Fitness & Gym - Flask Web Application
=============================================
A fitness and gym management web application built with Flask.
Provides client management, workout tracking, AI-style program generation,
membership management, and BMI calculation.
"""

from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import random
from datetime import datetime, date

# ---------------------------------------------------------------------------
# App & Config
# ---------------------------------------------------------------------------
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "aceest_fitness.db")

# ---------------------------------------------------------------------------
# Program data (mirrors the original Tkinter version)
# ---------------------------------------------------------------------------
PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "desc": "3-day full-body fat loss",
        "workouts": [
            "Mon: Back Squat 5x5 + Core",
            "Wed: Bench Press + 21-15-9",
            "Fri: Zone 2 Cardio 30min",
        ],
        "diet": "Breakfast: Egg Whites + Oats | Lunch: Grilled Chicken + Brown Rice | Dinner: Fish Curry + Millet Roti | Target: ~2000 kcal",
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "desc": "5-day split, higher volume fat loss",
        "workouts": [
            "Mon: Back Squat 5x5 + Core",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: Deadlift + Box Jumps",
            "Fri: Zone 2 Cardio 30min",
        ],
        "diet": "Breakfast: Egg Whites + Oats | Lunch: Grilled Chicken + Brown Rice | Dinner: Fish Curry + Millet Roti | Target: ~2400 kcal",
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy",
        "workouts": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10",
        ],
        "diet": "Breakfast: Eggs + PB Oats | Lunch: Chicken Biryani | Dinner: Mutton Curry + Rice | Target: ~3200 kcal",
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "3-day simple beginner full-body",
        "workouts": [
            "Mon: Air Squats + Push-ups",
            "Wed: Ring Rows + Lunges",
            "Fri: Plank + Light Deadlift",
        ],
        "diet": "Balanced Meals: Idli/Dosa/Rice + Dal | Protein Target: 120g/day",
    },
}

EXERCISE_POOL = {
    "Strength": ["Squat", "Deadlift", "Bench Press", "Overhead Press", "Pull-Up", "Barbell Row"],
    "Hypertrophy": ["Leg Press", "Incline Dumbbell Press", "Lat Pulldown", "Lateral Raise", "Bicep Curl", "Tricep Extension"],
    "Conditioning": ["Running", "Cycling", "Rowing", "Burpees", "Jump Rope", "Kettlebell Swings"],
    "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank", "Dumbbell Row", "Dumbbell Press"],
}

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    """Return a new database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all required tables if they do not exist."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_expiry TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
    """)

    # Default admin user
    cur.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin", "Admin"),
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Pure-logic / utility functions (easily testable)
# ---------------------------------------------------------------------------

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Return BMI given weight in kg and height in cm."""
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 2)


def bmi_category(bmi: float) -> str:
    """Return the WHO BMI category string."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def estimate_calories(weight_kg: float, program_name: str) -> int:
    """Estimate daily calorie needs based on weight and program."""
    program = PROGRAMS.get(program_name)
    if program is None:
        raise ValueError(f"Unknown program: {program_name}")
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    return int(weight_kg * program["factor"])


def generate_ai_program(program_name: str, experience: str) -> list:
    """
    Generate an AI-style workout program.
    Returns a list of dicts: [{day, exercise, sets, reps}, ...]
    """
    experience = experience.lower()
    if experience not in ("beginner", "intermediate", "advanced"):
        raise ValueError("Experience must be beginner, intermediate, or advanced")

    # Determine focus based on program name
    focus = "Full Body"
    if "Fat Loss" in program_name:
        focus = "Conditioning"
    elif "Muscle Gain" in program_name:
        focus = "Hypertrophy"

    if experience == "beginner":
        sets_range, reps_range, days = (2, 3), (8, 12), 3
    elif experience == "intermediate":
        sets_range, reps_range, days = (3, 4), (8, 15), 4
    else:
        sets_range, reps_range, days = (4, 5), (6, 15), 5

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:days]
    exercises_per_day = 3 if days < 4 else 4

    result = []
    for day in day_names:
        exercises = random.sample(EXERCISE_POOL[focus], k=exercises_per_day)
        for ex in exercises:
            result.append({
                "day": day,
                "exercise": ex,
                "sets": random.randint(*sets_range),
                "reps": random.randint(*reps_range),
            })
    return result


# ---------------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health-check endpoint for CI/CD and container orchestration."""
    return jsonify({"status": "healthy", "app": "ACEest Fitness & Gym"})


# ---- Programs -----------------------------------------------------------

@app.route("/api/programs", methods=["GET"])
def list_programs():
    """Return all available programs."""
    return jsonify(
        {name: {"desc": p["desc"], "factor": p["factor"]} for name, p in PROGRAMS.items()}
    )


# ---- Clients ------------------------------------------------------------

@app.route("/api/clients", methods=["GET"])
def get_clients():
    """Return a list of all clients."""
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients])


@app.route("/api/clients", methods=["POST"])
def create_client():
    """Create or update a client."""
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    age = data.get("age", 0)
    height = data.get("height", 0)
    weight = data.get("weight", 0)
    program = data.get("program", "")
    membership_expiry = data.get("membership_expiry", "")

    calories = None
    if weight and weight > 0 and program in PROGRAMS:
        calories = estimate_calories(weight, program)

    conn = get_db()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO clients
               (name, age, height, weight, program, calories, membership_expiry)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, age, height, weight, program, calories, membership_expiry),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": f"Client '{name}' saved", "calories": calories}), 201


@app.route("/api/clients/<name>", methods=["GET"])
def get_client(name):
    """Get a single client by name."""
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    conn.close()
    if client is None:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client))


@app.route("/api/clients/<name>", methods=["DELETE"])
def delete_client(name):
    """Delete a client by name."""
    conn = get_db()
    conn.execute("DELETE FROM clients WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client '{name}' deleted"})


# ---- Workouts -----------------------------------------------------------

@app.route("/api/workouts/<client_name>", methods=["GET"])
def get_workouts(client_name):
    """Return workouts for a given client."""
    conn = get_db()
    workouts = conn.execute(
        "SELECT * FROM workouts WHERE client_name = ? ORDER BY date DESC",
        (client_name,),
    ).fetchall()
    conn.close()
    return jsonify([dict(w) for w in workouts])


@app.route("/api/workouts", methods=["POST"])
def create_workout():
    """Log a workout for a client."""
    data = request.get_json(force=True)
    client_name = data.get("client_name", "").strip()
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400

    workout_date = data.get("date", date.today().isoformat())
    workout_type = data.get("workout_type", "General")
    duration = data.get("duration_min", 60)
    notes = data.get("notes", "")

    conn = get_db()
    conn.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
        (client_name, workout_date, workout_type, duration, notes),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout logged"}), 201


# ---- BMI ----------------------------------------------------------------

@app.route("/api/bmi", methods=["POST"])
def bmi_endpoint():
    """Calculate BMI from weight (kg) and height (cm)."""
    data = request.get_json(force=True)
    try:
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
        bmi = calculate_bmi(weight, height)
        return jsonify({"bmi": bmi, "category": bmi_category(bmi)})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


# ---- AI program ---------------------------------------------------------

@app.route("/api/generate-program", methods=["POST"])
def generate_program_endpoint():
    """Generate an AI-style workout program."""
    data = request.get_json(force=True)
    program_name = data.get("program", "")
    experience = data.get("experience", "beginner")
    try:
        plan = generate_ai_program(program_name, experience)
        return jsonify({"program": plan})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# ---- Membership ---------------------------------------------------------

@app.route("/api/membership/<client_name>", methods=["GET"])
def check_membership(client_name):
    """Check membership status of a client."""
    conn = get_db()
    client = conn.execute(
        "SELECT membership_expiry FROM clients WHERE name = ?", (client_name,)
    ).fetchone()
    conn.close()
    if client is None:
        return jsonify({"error": "Client not found"}), 404

    expiry = client["membership_expiry"]
    if expiry:
        try:
            exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            is_active = exp_date >= date.today()
        except ValueError:
            is_active = False
    else:
        is_active = False

    return jsonify({
        "client": client_name,
        "membership_expiry": expiry or "N/A",
        "is_active": is_active,
    })


# ---------------------------------------------------------------------------
# Application entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
