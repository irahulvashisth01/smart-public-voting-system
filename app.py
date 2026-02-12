from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

from face_module.capture import capture_images
from face_module.train import train_model
from face_module.verify import verify_face

app = Flask(__name__)
app.secret_key = "super_secret_key"


# =========================
# DATABASE INITIALIZATION
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # Citizens
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        voter_id TEXT UNIQUE NOT NULL,
        has_voted INTEGER DEFAULT 0
    )
    """)

    # Candidates
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        party TEXT NOT NULL
    )
    """)

    # Votes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citizen_id INTEGER,
        candidate_id INTEGER,
        FOREIGN KEY(citizen_id) REFERENCES citizens(id),
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        UNIQUE(citizen_id)
    )
    """)

    # Admin
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Election Control
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS election (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT DEFAULT 'stopped'
    )
    """)

    # Insert default admin
    cursor.execute("SELECT * FROM admin")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    # Insert default election row
    cursor.execute("SELECT * FROM election")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO election (status) VALUES ('stopped')")

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("home.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        voter_id = request.form.get("voter_id")

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
            "INSERT INTO citizens (name, voter_id) VALUES (?, ?)",
            (name.strip(), voter_id.strip())
            )

            conn.commit()

            citizen_id = cursor.lastrowid
            conn.close()

            capture_images(citizen_id)
            train_model()

            return render_template("register.html", message="Registration Successful!")

        except sqlite3.IntegrityError:
            return render_template("register.html", message="Voter ID already exists!")

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        voter_id = request.form["voter_id"].strip()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, has_voted FROM citizens WHERE voter_id=?", (voter_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            predicted_id = verify_face()

            if predicted_id == user[0]:
                if user[1] == 1:
                    return render_template("login.html", message="You have already voted!")

                session["citizen_id"] = user[0]
                return redirect("/vote")
            else:
                return render_template("login.html", message="Face not matched!")
        else:
            return render_template("login.html", message="Invalid Voter ID!")

    return render_template("login.html")



# =========================
# VOTE
# =========================
@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "citizen_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    citizen_id = session["citizen_id"]

    # Get voter info
    cursor.execute("SELECT name, voter_id, has_voted FROM citizens WHERE id=?", (citizen_id,))
    voter = cursor.fetchone()
    has_voted = voter[2]

    # Get candidates
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    voted_candidate_id = None

    # If already voted, find whom they voted
    if has_voted:
        cursor.execute("SELECT candidate_id FROM votes WHERE citizen_id=?", (citizen_id,))
        vote_record = cursor.fetchone()
        if vote_record:
            voted_candidate_id = vote_record[0]

    if request.method == "POST" and not has_voted:
        candidate_id = request.form["candidate"]

        cursor.execute(
            "INSERT INTO votes (citizen_id, candidate_id) VALUES (?, ?)",
            (citizen_id, candidate_id)
        )
        cursor.execute("UPDATE citizens SET has_voted=1 WHERE id=?", (citizen_id,))
        conn.commit()

        return redirect("/vote")

    conn.close()

    return render_template(
        "vote.html",
        candidates=candidates,
        voter=voter,
        has_voted=has_voted,
        voted_candidate_id=voted_candidate_id
    )




# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        party = request.form["party"]
        cursor.execute("INSERT INTO candidates (name, party) VALUES (?, ?)", (name, party))
        conn.commit()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    cursor.execute("SELECT status FROM election LIMIT 1")
    status = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM citizens")
    total_voters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM votes")
    total_votes = cursor.fetchone()[0]

    conn.close()

    return render_template("admin.html",
                           candidates=candidates,
                           status=status,
                           total_voters=total_voters,
                           total_votes=total_votes)


# =========================
# EDIT CANDIDATE
# =========================
@app.route("/edit_candidate/<int:id>", methods=["GET", "POST"])
def edit_candidate(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        party = request.form["party"]
        cursor.execute("UPDATE candidates SET name=?, party=? WHERE id=?", (name, party, id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    cursor.execute("SELECT * FROM candidates WHERE id=?", (id,))
    candidate = cursor.fetchone()
    conn.close()

    return render_template("edit_candidate.html", candidate=candidate)


# =========================
# DELETE CANDIDATE
# =========================
@app.route("/delete_candidate/<int:id>")
def delete_candidate(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# START / STOP / RESET
# =========================
@app.route("/start_election")
def start_election():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE election SET status='running'")
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/stop_election")
def stop_election():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE election SET status='stopped'")
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/reset_election")
def reset_election():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votes")
    cursor.execute("UPDATE citizens SET has_voted=0")
    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# RESULTS
# =========================
@app.route("/results")
def results():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidates.name, COUNT(votes.id) as total_votes
        FROM candidates
        LEFT JOIN votes ON votes.candidate_id = candidates.id
        GROUP BY candidates.id
    """)

    results = cursor.fetchall()

    # Calculate total votes
    total_votes = sum([row[1] for row in results])

    # Detect winner
    winner = None
    if results:
        winner = max(results, key=lambda x: x[1])[0]

    conn.close()

    return render_template(
        "results.html",
        results=results,
        total_votes=total_votes,
        winner=winner
    )

@app.route("/export_pdf")
def export_pdf():

    # Admin Security Check
    if not session.get("admin"):
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidates.name, COUNT(votes.id)
        FROM candidates
        LEFT JOIN votes ON votes.candidate_id = candidates.id
        GROUP BY candidates.id
    """)

    data = cursor.fetchall()
    conn.close()

    # Create PDF File
    file_path = "election_results.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    # Table Data
    table_data = [["Candidate", "Total Votes"]]
    for row in data:
        table_data.append([row[0], row[1]])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))

    elements = []
    elements.append(table)

    doc.build(elements)

    return send_file(file_path, as_attachment=True)




# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
