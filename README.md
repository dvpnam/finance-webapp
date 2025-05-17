# 💰 Finance Webapp

> A dynamic stock trading simulator built with Flask — inspired by real-world brokerage apps and developed as part of Harvard's CS50 curriculum.

---

## 🧠 Overview

This web application allows users to:

- Register and log in securely
- Get real-time stock quotes
- Buy and sell stocks
- View current portfolio with real-time pricing
- Track transaction history
- Deposit cash

Built with a focus on clarity, simplicity, and real-world application of the MVC (Model-View-Controller) pattern using Python and Flask.

---

## 🏗️ Tech Stack

| Layer      | Technology          |
|------------|---------------------|
| Frontend   | HTML, CSS (custom), Jinja2 templating |
| Backend    | Python, Flask       |
| Database   | SQLite (via CS50 Library) |
| API        | IEX Cloud (stock data) |

---

## 🧭 Project Structure

finance/
├── app.py               # Flask application logic (Controller)
├── helpers.py           # Business logic and API wrappers
├── templates/           # HTML files (View)
│   ├── layout.html
│   ├── index.html
│   └── …
├── static/styles.css    # Custom styling
├── finance.db           # SQLite database (Model)
└── requirements.txt     # Python dependencies

---

## 🚀 Features

- 🔐 User authentication with password hashing
- 📈 Live stock quotes from IEX API
- 🛒 Buy/sell with balance and validation checks
- 📊 Portfolio summary with total asset calculation
- 📜 Transaction log (history)
- 💸 Add cash to simulate deposits

---

## 🧠 Learning Highlights

- Implemented Flask sessions for user login state
- Used SQL for persistent data storage with transactions
- Separated logic into views, routes, and helpers (MVC)
- API error handling and user feedback via `apology()` system
- CSS customization for improved UX

---

## 🚧 Future Enhancements

- Switch from SQLite to PostgreSQL
- Responsive design using Tailwind or Bootstrap
- Add "Watchlist" and email alerts
- Dockerize for production deployment

---

## 📸 Screenshots

> *(Add screenshots here if possible — login page, dashboard, buy form, etc.)*

---

## 🧑‍💻 Author

**Nam Dao**  
Aspiring Software Engineer | CS50x 2024 Student  
[GitHub](https://github.com/dvpnam) • [LinkedIn](#) *(optional)*

---

## 📜 License

MIT — because knowledge should be free.
