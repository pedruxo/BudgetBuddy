import os
import json
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response, send_file
from datetime import datetime
import uuid


app = Flask(__name__)
DATA_FILE = "expenses.json"

months_names = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
    }

def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def save_expenses(expenses):
    with open(DATA_FILE, 'w') as file:
        json.dump(expenses, file, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():

    expenses = load_expenses()

    filtered_expenses = expenses
    total_filtered_expenses = expenses

    month_name = None
    month = None
    year = None

    if request.method == "POST":
        month = request.form.get("month")
        year = request.form.get("year")

        if month and year:
            filtered_expenses = [
                expense for expense in expenses
                if expense['date'].startswith(f"{year}-{month}")
            ]
            month_name = months_names.get(month, None)

    total_all_expenses = sum(
        expense['amount'] for expense in expenses
        if isinstance(expense.get('amount'), (int, float))
    )

    total_filtered_expenses = sum(
        expense['amount'] for expense in filtered_expenses
        if isinstance(expense.get('amount'), (int, float))
    )

    category_totals_all = {}

    for expense in expenses:
        category_totals_all[expense['category']] = category_totals_all.get(
            expense['category'], 0
        ) + expense['amount']

    return render_template("index.html", all_expenses=expenses, filtered_expenses=filtered_expenses, total_all_expenses=total_all_expenses, total_filtered_expenses=total_filtered_expenses, category_totals=category_totals_all, month_name=month_name, month=month, year=year)

@app.route("/add", methods=["POST"])
def add_expense():
    description = request.form.get("description")
    amount = request.form.get("amount")
    category = request.form.get("category")
    date = request.form.get("date")
    details = request.form.get("details")

    if description and amount and category:
        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError("Amount must be positive. Try again.")

            if not date:
                date = datetime.today().strftime("%Y-%m-%d")

            new_expense = {
                "id": str(uuid.uuid4()),
                "description": description,
                "amount": amount,
                "category": category,
                "date": date,
                "details": details or ""
            }
            expenses = load_expenses()
            expenses.append(new_expense)
            save_expenses(expenses)

        except ValueError as e:
            return render_template(
                "index.html",
                expenses=load_expenses(),
                total=sum(item["amount"] for item in load_expenses()),
                error=str(e)
            )

    else:
        return render_template(
            "index.html",
            expenses=load_expenses(),
            total=sum(item["amount"] for item in load_expenses()),
            error="All fields are required."
        )
    return redirect(url_for("index"))

@app.route("/edit/<expense_id>", methods=["GET"])
def edit_expense(expense_id):
    expenses = load_expenses()
    expense_edit = next((expense for expense in expenses if expense['id'] == expense_id), None)

    if not expense_edit:
        return "Expense not found", 404

    return render_template("edit.html", expense=expense_edit)

@app.route("/update/<expense_id>", methods=["POST"])
def update_expense(expense_id):
    expenses = load_expenses()

    for expense in expenses:
        if expense['id'] == expense_id:
            expense['description'] = request.form['description']
            expense['amount'] = float(request.form['amount'])
            expense['category'] = request.form['category']
            expense['date'] = request.form['date']
            expense['details'] == request.form.get('details', "")
            break

    save_expenses(expenses)
    return redirect(url_for("index"))

@app.route("/delete/<expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expenses = load_expenses()

    expenses = [expense for expense in expenses if expense['id'] != expense_id]

    save_expenses(expenses)
    return redirect(url_for("index"))

@app.route("/clear", methods=["POST"])
def clear_expenses():
    save_expenses([])
    return redirect(url_for("index"))

@app.route("/export_csv", methods=["GET"])
def export_csv():
    expenses = load_expenses()
    csv_filename = "expenses.csv"

    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Description", "Amount", "Category", "Date", "Details"])

        for expense in expenses:
            writer.writerow([
                expense.get("id", ""),
                expense["description"],
                expense["amount"],
                expense["category"],
                expense["date"],
                expense.get("details", "")
            ])

    return send_file(csv_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
