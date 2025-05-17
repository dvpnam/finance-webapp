import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Lấy ID người dùng hiện tại
    user_id = session["user_id"]

    # Lấy thông tin cổ phiếu từ cơ sở dữ liệu
    rows = db.execute(
        """
        SELECT symbol, SUM(shares) AS total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
        """,
        user_id,
    )

    # Lấy số tiền mặt còn lại
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Danh sách lưu trữ thông tin cổ phiếu
    portfolio = []
    total_value = cash

    # Lấy thông tin giá cổ phiếu và tính toán tổng giá trị
    for row in rows:
        quote = lookup(row["symbol"])  # Gọi API lấy giá cổ phiếu hiện tại
        price = quote["price"]
        total = price * row["total_shares"]
        total_value += total

        # Thêm thông tin vào danh mục đầu tư
        portfolio.append(
            {
                "symbol": row["symbol"],
                "shares": row["total_shares"],
                "price": usd(price),
                "total": usd(total),
            }
        )

    return render_template(
        "index.html", portfolio=portfolio, cash=usd(cash), total=usd(total_value)
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol", 400)

        shares = request.form.get("shares")
        if not shares:
            return apology("missing shares", 400)

        try:
            shares = int(shares)

            if shares <= 0:
                return apology("invalid shares", 400)
        except ValueError:
            return apology("invalid shares", 400)

        user_id = session["user_id"]
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        total = stock["price"] * int(shares)
        if total > user_cash:
            return apology("can't afford", 400)

        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            stock["symbol"],
            shares,
            stock["price"],
        )

        flash("Bought!")
        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Lấy user_id từ phiên đăng nhập
    user_id = session["user_id"]

    # Truy xuất tất cả giao dịch của người dùng
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ?", user_id)

    # Chuyển hướng đến trang history.html với dữ liệu giao dịch
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol", 400)

        return render_template(
            "quoted.html",
            name=stock["name"],
            symbol=stock["symbol"],
            price=stock["price"]
        )

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("missing username", 400)

        password = request.form.get("password")
        if not password:
            return apology("missing password", 400)

        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("passwords don't match", 400)

        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                username, generate_password_hash(password)
            )
        except ValueError:
            return apology("username taken", 400)

        flash("Register!")
        return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        # Lấy symbol từ form
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)

        # Kiểm tra người dùng có sở hữu cổ phiếu này không
        user_id = session["user_id"]
        user_shares = db.execute(
            "SELECT SUM(shares) as shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id,
            symbol,
        )

        # Lấy số lượng cổ phiếu muốn bán
        shares = request.form.get("shares")
        shares = int(shares)

        # Kiểm tra xem người dùng có đủ cổ phiếu để bán không
        owned_shares = user_shares[0]["shares"]
        if shares > owned_shares:
            return apology("too many shares", 400)

        # Lấy thông tin giá cổ phiếu
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol", 400)

        # Tính tổng tiền thu được từ việc bán
        total_revenue = stock["price"] * shares

        # Ghi nhận giao dịch bán
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            symbol,
            -shares,
            stock["price"],
        )

        # Cộng tiền vào tài khoản người dùng
        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?", total_revenue, user_id
        )

        flash("Sold!")
        # Chuyển hướng về trang chủ
        return redirect("/")

    # Lấy danh sách các cổ phiếu mà người dùng sở hữu
    user_id = session["user_id"]
    portfolio = db.execute(
        "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0",
        user_id,
    )

    return render_template("sell.html", portfolio=portfolio)
