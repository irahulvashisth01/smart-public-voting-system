 🏛 Smart Public Voting System

A secure and modern web-based voting system with biometric authentication, admin control panel, live results dashboard, and PDF export functionality.

🔗 **Live Demo:**  
https://smart-public-voting-system.onrender.com/

📌 Project Overview

The Smart Public Voting System is a secure election management platform developed using Flask.  
It ensures one-person-one-vote enforcement with biometric authentication and provides a professional admin dashboard for election control.

This project demonstrates backend development, authentication systems, database management, deployment, and UI design.

✨ Key Features

👤 Voter Features
- Voter registration
- Biometric authentication (local version)
- Secure login system
- One-person-one-vote enforcement
- Live voting interface
- View election results

🛠 Admin Features
- Admin authentication
- Start / Stop election
- Reset election data
- Add / Edit / Delete candidates
- View total voters & vote statistics
- Auto-detect winner
- Live vote percentage bars
- Graph-based results dashboard
- Export election results to PDF

📊 Results Dashboard
- Live vote count
- Percentage progress bars
- Winner auto-highlight
- Bar chart visualization
- Secure admin-only PDF export

🧠 Tech Stack

Backend
- Python
- Flask
- SQLite
- Gunicorn (Production server)

Frontend
- HTML5
- CSS3
- Bootstrap 5
- Chart.js

Additional Libraries
- OpenCV (Face Recognition - Local Version)
- ReportLab (PDF Export)
- Jinja2

Deployment
- GitHub
- Render (Cloud Hosting)

🏗 System Architecture

User → Flask Server → SQLite Database  
Admin → Dashboard Control → Election Management  
Results → Chart.js Visualization → PDF Export

🔐 Security Features

- Session-based authentication
- Admin role verification
- One-vote-per-user enforcement
- Protected admin routes
- Secure deployment with Gunicorn

📷 Screenshots

🏠 Home Page
<img width="1755" height="1196" alt="image" src="https://github.com/user-attachments/assets/cba46492-68f6-4614-a6dc-25e596d2b74f" />


🗳 Voting Interface
<img width="1755" height="918" alt="image" src="https://github.com/user-attachments/assets/87fa2832-ca45-4f3d-adea-322801910cbe" />


🛠 Admin Dashboard
<img width="1755" height="1339" alt="image" src="https://github.com/user-attachments/assets/02e3102a-9f60-440a-9b31-59df2f86af28" />


📊 Results Dashboard
<img width="1755" height="1595" alt="image" src="https://github.com/user-attachments/assets/a16caf44-53e2-4bbc-b27e-90f001d3465e" />


🚀 How To Run Locally

1. Clone repository:
https://github.com/irahulvashisth01/smart-public-voting-system.git

2. Install dependencies:
pip install -r requirements.txt

3. Run application:
python app.py

4. Open:
http://127.0.0.1:5000/



📈 Future Improvements

- PostgreSQL integration
- Image upload-based cloud biometric system
- Role-based multi-admin control
- Blockchain vote hashing
- Real-time WebSocket updates
- Dark mode toggle
- API version


👨‍💻 Developer

**Rahul Sharma**  
B.Tech CSE Student  
GitHub: https://github.com/irahulvashisth01

**Utkarsh Mishra**
B.Tech CSE Student
Github: https://github.com/iamutkarshmishra740-ops



📜 License

This project is developed for educational and academic purposes.

