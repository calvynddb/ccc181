"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import sys

from flask import Flask, render_template

if sys.version_info.releaselevel != "final":
    raise RuntimeError(
        "Mito requires a stable Python release. This project is pinned to Python 3.13.12; "
        f"the active interpreter is {sys.version.split()[0]}. Select the workspace .venv interpreter."
    )
if sys.version_info < (3, 11):
    raise RuntimeError("Mito requires Python 3.11 or newer.")

app = Flask(__name__)
app.secret_key = "dev-only-change-me"

SERVICES = [
    {"id": 1, "name": "PC session"},
]

TICKETS = [
    {
        "number": 1,
        "nickname": "Ana",
        "phone": None,
        "service_id": 1,
        "status": "waiting",
    },
    {
        "number": 2,
        "nickname": "Ben",
        "phone": None,
        "service_id": 1,
        "status": "waiting",
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    return render_template("join.html")


@app.get("/staff")
def staff_dashboard():
    return render_template("staff.html")


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    return render_template("ticket.html", ticket_id=ticket_id)


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
