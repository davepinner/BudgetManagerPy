from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from datetime import date, datetime, timedelta
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import BudgetStylwForm, MemberForm, BankForm, BankEditForm, LoginForm, RegisterForm, IncomeForm, \
    OutgoingForm, SubCategoryForm, VariableForm, TransferForm, ForecastForm, ActualSettingForm
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = "sdghdfdgfhs"

# Connect to the database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///budgetmanager.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Budget(db.Model):
    __tablename__ = 'budget'
    bmID = db.Column(db.Integer, primary_key=True)
    budgettype = db.Column(db.String(100), nullable=False)
    users = relationship("User")
    banks = relationship("Bank")
    incomes = relationship("Income")
    outgoings = relationship("Outgoing")
    variable = relationship("Variable")
    transaction = relationship("Transaction")
    forecast = relationship("Forecast")
    actual = relationship("Actual")
    transfer = relationship("Transfer")
    graph = relationship("Graph")


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(100))


class Bank(db.Model):
    __tablename__ = 'bank'
    bankID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    bankname = db.Column(db.String(100), nullable=False)
    accounttype = db.Column(db.String(100), nullable=False)
    currentbalance = db.Column(db.Float, nullable=False)
    startingbalance = db.Column(db.Float, nullable=False)
    balanceupdatedate = db.Column(db.Date, nullable=True)


class Forecast(db.Model):
    __tablename__ = "forecast"
    fctID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    forecastname = db.Column(db.String(100), nullable=False)
    length = db.Column(db.String(100), nullable=False)
    forecastdate = db.Column(db.Date, nullable=True)
    incomevariation = db.Column(db.Integer, nullable=True)
    outgoingvariation = db.Column(db.Integer, nullable=True)
    transaction = relationship("Transaction", cascade='all,delete')


class Actual(db.Model):
    __tablename__ = "actual"
    actID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    transaction = relationship("Transaction")


class Transaction(db.Model):
    __tablename__ = "transaction"
    trnID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    fctID = db.Column(db.Integer, db.ForeignKey('forecast.fctID'), nullable=True)
    actID = db.Column(db.Integer, db.ForeignKey('actual.actID'), nullable=True)
    type = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Integer, nullable=True)
    subcategory = db.Column(db.Integer, nullable=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=True)


class Income(db.Model):
    __tablename__ = 'income'
    incID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    paidinto = db.Column(db.Integer, nullable=False)
    nextduedate = db.Column(db.Integer, nullable=False)


class Outgoing(db.Model):
    __tablename__ = 'outgoing'
    outID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    nextduedate = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    subcategory = db.Column(db.Integer, nullable=False)
    paidfrom = db.Column(db.Integer, nullable=False)


class Variable(db.Model):
    __tablename__ = 'variable'
    varID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Integer, nullable=False)
    subcategory = db.Column(db.Integer, nullable=False)


class Transfer(db.Model):
    __tablename__ = 'transfer'
    trnID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    accountfrom = db.Column(db.Integer, nullable=False)
    accountto = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    nextduedate = db.Column(db.Integer, nullable=False)


class Graph(db.Model):
    __tablename__ = 'graph'
    grpID = db.Column(db.Integer, primary_key=True)
    bmID = db.Column(db.Integer, db.ForeignKey('budget.bmID'), nullable=False)
    graphdate = db.Column(db.Date, nullable=False)
    graphtype = db.Column(db.String(100), nullable=False)
    datapoint = relationship("DataPoint")


class DataPoint(db.Model):
    __tablename__ = 'datapoint'
    dpID = db.Column(db.Integer, primary_key=True)
    grpID = db.Column(db.Integer, db.ForeignKey('graph.grpID'), nullable=False)
    bankID = db.Column(db.Integer, nullable=False)
    pointdate = db.Column(db.Date, nullable=False)
    balance = db.Column(db.Float, nullable=False)


class OutgoingCategory(db.Model):
    __tablename__ = 'outgoingcategory'
    catID = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(100), nullable=False)
    child = relationship("SubCategory")


class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    subID = db.Column(db.Integer, primary_key=True)
    parentcategory = db.Column(db.Integer, db.ForeignKey('outgoingcategory.catID'), nullable=False)
    subcategoryname = db.Column(db.String(100), nullable=False)


db.create_all()

# # Run this only once to create the core categories in the database
if not OutgoingCategory.query.all():
    parent_categories = ["Food",
                         "Utilities",
                         "Housing",
                         "Insurance",
                         "Credit",
                         "Transportation",
                         "Entertainment",
                         "Miscellaneous",
                         "Savings",
                         "Holidays"
    ]
    for cat in parent_categories:
        category = OutgoingCategory(
            categoryname=cat
        )
        db.session.add(category)
        db.session.commit()

    sub_categories = [
        [1, "Groceries"], [1, "Eating Out"],
        [2, "Gas"], [2, "Electricity"], [2, "Water"], [2, "Council Tax"],
        [3, "Mortgage"], [3, "Rent"],
        [4, "Car"], [4, "Home"], [4, "Health"],
        [5, "Loan"], [5, "Credit Card"],
        [6, "Car Fuel"], [6, "Travel"], [6, "Commuting"],
        [7, "Hobbies"], [7, "Gym"], [7, "Nights Out"], [7, "Media Subscriptions"],
        [8, "Birthdays"],
    ]
    for sub in sub_categories:
        sub_category = SubCategory(
            parentcategory=sub[0],
            subcategoryname=sub[1]
        )
        db.session.add(sub_category)
        db.session.commit()


def create_transactions(months, forecast, actual):
    current_day = date.today()
    end_date = get_end_date(months, current_day)
    if forecast:
        transaction_type = "forecast"
    else:
        transaction_type = "actual"

    while current_day <= end_date:
        current_day_num = current_day.day
        # apply incomes
        # fetch the incomes for this budget
        incomes = Income.query.filter_by(bmID=current_user.bmID)
        for income in incomes:
            if income.nextduedate == current_day_num:
                new_transaction = Transaction(
                    bmID=current_user.bmID,
                    fctID=forecast.fctID,
                    actID=actual.actID,
                    type=transaction_type,
                    date=current_day,
                    amount=income.amount,
                    account=income.paidinto
                )
                db.session.add(new_transaction)
                db.session.commit()
                # increment the nextduedate month

        # apply outgoings
        outgoings = Outgoing.query.filter_by(bmID=current_user.bmID)
        current_ac = Bank.query.filter_by(accounttype="Current").first()
        for outgoing in outgoings:
            if outgoing.nextduedate == current_day_num:
                new_transaction = Transaction(
                    bmID=current_user.bmID,
                    fctID=forecast.fctID,
                    actID=actual.actID,
                    type=transaction_type,
                    date=current_day,
                    category=outgoing.category,
                    subcategory=outgoing.subcategory,
                    amount=outgoing.amount * -1,
                    account=outgoing.paidfrom
                )
                db.session.add(new_transaction)
                db.session.commit()
                # increment the nextduedate month

        # apply variables - account for daily, weekly and monthly
        variables = Variable.query.filter_by(bmID=current_user.bmID)
        for variable in variables:
            if variable.frequency == "Daily":
                new_transaction = Transaction(
                    bmID=current_user.bmID,
                    fctID=forecast.fctID,
                    actID=actual.actID,
                    type=transaction_type,
                    date=current_day,
                    category=variable.category,
                    subcategory=variable.subcategory,
                    amount=variable.amount * -1,
                    account=current_ac.bankID
                )
                db.session.add(new_transaction)
                db.session.commit()
            elif variable.frequency == "Weekly":
                if is_saturday(current_day):
                    new_transaction = Transaction(
                        bmID=current_user.bmID,
                        fctID=forecast.fctID,
                        actID=actual.actID,
                        type=transaction_type,
                        date=current_day,
                        category=variable.category,
                        subcategory=variable.subcategory,
                        amount=variable.amount * -1,
                        account=current_ac.bankID
                    )
                    db.session.add(new_transaction)
                    db.session.commit()
            elif variable.frequency == "Monthly":
                if current_day.day == 1:
                    new_transaction = Transaction(
                        bmID=current_user.bmID,
                        fctID=forecast.fctID,
                        actID=actual.actID,
                        type=transaction_type,
                        date=current_day,
                        category=variable.category,
                        subcategory=variable.subcategory,
                        amount=variable.amount * -1,
                        account=current_ac.bankID
                    )
                    db.session.add(new_transaction)
                    db.session.commit()


        # apply transfers
        transfers = Transfer.query.filter_by(bmID=current_user.bmID)
        for transfer in transfers:
            if transfer.nextduedate == current_day_num:
                new_to_transaction = Transaction(
                    bmID=current_user.bmID,
                    fctID=forecast.fctID,
                    actID=actual.actID,
                    type=transaction_type,
                    date=current_day,
                    amount=transfer.amount,
                    account=transfer.accountto
                )
                db.session.add(new_to_transaction)
                db.session.commit()
                new_from_transaction = Transaction(
                    bmID=current_user.bmID,
                    fctID=forecast.fctID,
                    actID=actual.actID,
                    type=transaction_type,
                    date=current_day,
                    amount=transfer.amount * -1,
                    account=transfer.accountfrom
                )
                db.session.add(new_from_transaction)
                db.session.commit()

        current_day = current_day + timedelta(days=1)


def add_balances(accounts, forecast_id):
    transactions = Transaction.query.filter_by(fctID=forecast_id).order_by(Transaction.date)
    for account in accounts:
        balance = account.currentbalance
        for trn in transactions:
            if trn.account == account.bankID:
                balance += trn.amount
                trn.balance = balance
                db.session.commit()


def increment_date(due_date):
    return due_date + timedelta(days=1)


def get_end_date(months, today):
    end_month = today.month + int(months)
    if end_month > 12:
        end_month -= 12
        end_date = date(today.year + 1, end_month,  today.day)
    else:
        end_date = date(today.year, end_month,  today.day)
    return end_date


def get_closing_balances(months):
    accounts = Bank.query.filter_by(bmID=current_user.bmID)
    end_date = get_end_date(months, date.today())
    account_forecasts = []
    for account in accounts:
        transactions = Transaction.query.filter(
            Transaction.bmID == current_user.bmID,
            Transaction.account == account.bankID,
            Transaction.type == "forecast",
            end_date >= Transaction.date,
            Transaction.date >= date.today()
        )
        for trn in transactions:
            account.currentbalance += trn.amount
        account_forecasts.append(account.currentbalance)
        return account_forecasts


def is_saturday(current_date):
    return current_date.weekday() == 5


def profile_created():
    bank_count = Bank.query.filter_by(bmID=current_user.bmID).count()
    income_count = Income.query.filter_by(bmID=current_user.bmID).count()
    outgoing_count = Outgoing.query.filter_by(bmID=current_user.bmID).count()
    variable_count = Variable.query.filter_by(bmID=current_user.bmID).count()
    if bank_count > 0 and income_count > 0 and outgoing_count and variable_count > 0:
        return True


def create_data_points(transactions, graph_id, accounts):
    dp_collection = []
    for account in accounts:
        for transaction in transactions:
            if account.bankID == transaction.account:
                new_dp = DataPoint(
                    grpID=graph_id,
                    bankID=transaction.account,
                    pointdate=transaction.date,
                    balance=transaction.amount
                )
                db.session.add(new_dp)
                db.session.commit()
                dp_collection.append(new_dp)
    return dp_collection


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/budget-overview", methods=["GET", "POST"])
def budget_overview():
    if current_user.is_authenticated:
        user_count = User.query.filter_by(bmID=current_user.bmID).count()
        bank_count = Bank.query.filter_by(bmID=current_user.bmID).count()
        income_count = Income.query.filter_by(bmID=current_user.bmID).count()
        outgoing_count = Outgoing.query.filter_by(bmID=current_user.bmID).count()
        variable_count = Variable.query.filter_by(bmID=current_user.bmID).count()
        transfer_count = Transfer.query.filter_by(bmID=current_user.bmID).count()
        accounts = Bank.query.filter_by(bmID=current_user.bmID)
        budget = Budget.query.get(current_user.bmID)
        budget_type = budget.budgettype
        # if profile_created():
        #     create_transactions(1)
        return render_template(
            'budget-overview.html',
            user_count=user_count,
            budget_type=budget_type,
            bank_count=bank_count,
            income_count=income_count,
            outgoing_count=outgoing_count,
            accounts=accounts,
            closing_balance=get_closing_balances,
            variable_count=variable_count,
            transfer_count=transfer_count
        )
    return render_template('budget-overview.html')


@app.route("/forecasts", methods=["GET", "POST"])
def forecasts():
    forecasts = Forecast.query.filter_by(bmID=current_user.bmID)
    return render_template('forecasts.html', forecasts=forecasts)


@app.route("/add-forecast", methods=["GET", "POST"])
def add_forecast():
    form = ForecastForm()
    accounts = Bank.query.filter_by(bmID=current_user.bmID)
    if form.validate_on_submit():
        # Create a new Forecast instance
        new_forecast = Forecast(
            bmID=current_user.bmID,
            forecastname=form.name.data,
            length=form.project.data,
            incomevariation=form.vary_income.data,
            outgoingvariation=form.vary_outgoings.data,
            forecastdate=date.today(),
        )
        db.session.add(new_forecast)
        db.session.commit()
        # create the forecast transactions for the period defined from today
        create_transactions(form.project.data, forecast=new_forecast, None)
        return redirect(url_for('view_forecast', forecast_id=new_forecast.fctID))
    return render_template('add-forecast.html', form=form)


@app.route("/view-forecast/<int:forecast_id>", methods=["GET", "POST"])
def view_forecast(forecast_id):
    forecast = Forecast.query.get(forecast_id)
    accounts = Bank.query.filter_by(bmID=current_user.bmID)
    # update the transaction set with account balances
    add_balances(accounts, forecast_id)
    # get the transactions created and subsequently updated with the balance
    transactions = Transaction.query.filter_by(fctID=forecast_id).order_by(Transaction.date)
    # update the transaction set with account balances
    add_balances(accounts, forecast_id)
    return render_template('view-forecast.html', transactions=transactions, accounts=accounts, forecast=forecast)

    # new_graph = Graph(
    #     bmID=current_user.bmID,
    #     graphdate=date.today(),
    #     graphtype='forecast'
    # )
    # db.session.add(new_graph)
    # db.session.commit()
    # graph_id = new_graph.grpID
    # graph_data = create_data_points(transactions, graph_id, accounts)
    # s = pd.Series(graph_data)
    # fig, ax = plt.subplots()
    # s.plot.line()
    # graph = fig.savefig('my_plot.png')


@app.route("/delete-forecast/<forecast_id>")
def delete_forecast(forecast_id):
    # delete the forecast
    forecast_to_delete = Forecast.query.get(forecast_id)
    db.session.delete(forecast_to_delete)
    db.session.commit()
    return redirect(url_for("forecasts"))


@app.route("/actuals", methods=["GET", "POST"])
def view_actuals():
    accounts = Bank.query.filter_by(bmID=current_user.bmID)
    incomes = Income.query.filter_by(bmID=current_user.bmID)
    outgoings = Outgoing.query.filter_by(bmID=current_user.bmID)
    transfers = Transfer.query.filter_by(bmID=current_user.bmID)
    form = ActualSettingForm()
    if form.validate_on_submit():
        new_actual = Actual(
            bmID=current_user.bmID
        )
        db.session.add(new_actual)
        db.session.commit()
        return render_template("view-budget.html", new_actual)
    return render_template(
        "actuals.html",
        accounts=accounts,
        incomes=incomes,
        outgoings=outgoings,
        transfers=transfers,
        form=form
    )


@app.route("/view-budget", methods=["GET", "POST"])
def view_budget(actual):
    create_transactions(1, None, actual)

    return render_template("view-budget.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    budget = Budget.query.filter_by(bmID=current_user.bmID).first()
    return render_template("profile.html", budget=budget)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_budget = Budget(
            budgettype="weekly"
        )
        db.session.add(new_budget)
        db.session.commit()
        new_user = User(
            bmID=new_budget.bmID,
            email=form.email.data,
            firstname=form.firstname.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home", current_user=new_user))

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home', current_user=user))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/budget-style", methods=["GET", "POST"])
def budget_style():
    form = BudgetStylwForm()
    if form.validate_on_submit():
        new_profile = Budget(
            budgettype=form.type.data
        )
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("budget-style.html", form=form)


# Members
@app.route('/members', methods=["GET", "POST"])
def view_members():
    members = User.query.filter_by(bmID=current_user.bmID)
    return render_template('members.html', members=members)


@app.route("/add-member", methods=["GET", "POST"])
def add_member():
    form = MemberForm()
    if form.validate_on_submit():
        new_user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            bmID=current_user.bmID
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("view_members"))
    return render_template("add-member.html", form=form)


@app.route("/edit-member/<int:user_id>", methods=["GET", "POST"])
def edit_member(user_id):
    user = User.query.get(user_id)
    edit_form = MemberForm(
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email
    )
    if edit_form.validate_on_submit():
        user.firstname = edit_form.firstname.data
        user.lastname = edit_form.lastname.data
        user.email = edit_form.email.data
        db.session.commit()
        return redirect(url_for("view_members"))
    return render_template("add-member.html", form=edit_form, is_edit=True, current_user=current_user)


# Banks
@app.route("/view-banks", methods=["GET", "POST"])
def view_banks():
    banks = Bank.query.filter_by(bmID=current_user.bmID)
    return render_template("banks.html", banks=banks)


@app.route("/add-bank", methods=["GET", "POST"])
def add_bank():
    form = BankForm()
    if form.validate_on_submit():
        new_bank = Bank(
            bmID=current_user.bmID,
            bankname=form.bankname.data,
            accounttype=form.acctype.data,
            startingbalance=form.opening_balance.data,
            currentbalance=form.opening_balance.data
        )
        db.session.add(new_bank)
        db.session.commit()
        return redirect(url_for("view_banks"))
    return render_template('add-bank.html', form=form)


@app.route("/edit-bank/<bank_id>/<update>", methods=["GET", "POST"])
def edit_bank(bank_id, update):
    bank = Bank.query.get(bank_id)
    edit_form = BankEditForm(
        bankname=bank.bankname,
        acctype=bank.accounttype,
        updatedbalance=bank.currentbalance
    )
    if edit_form.validate_on_submit():
        bank.bankname=edit_form.bankname.data
        bank.accounttype=edit_form.acctype.data
        bank.currentbalance=edit_form.updated_balance.data
        db.session.commit()
        if update:
            return redirect(url_for('view_actuals'))
        else:
            return redirect(url_for('view_banks'))
    return render_template('add-bank.html', is_edit=True, form=edit_form, current_user=current_user)


@app.route("/delete-bank/<bank_id>")
def delete_bank(bank_id):
    bank_to_delete = Bank.query.get(bank_id)
    db.session.delete(bank_to_delete)
    db.session.commit()
    return redirect(url_for("view_banks"))


# Incomes
@app.route("/view-incomes", methods=["GET", "POST"])
def view_incomes():
    incomes = Income.query.filter_by(bmID=current_user.bmID)
    users = User.query.filter_by(bmID=current_user.bmID)
    return render_template('incomes.html', incomes=incomes, users=users, user_name=get_member_name)


@app.route("/add-income", methods=["GET", "POST"])
def add_income():
    form = IncomeForm()
    users = User.query.filter_by(bmID=current_user.bmID)
    form.owner.choices = [(user.id, user.firstname) for user in users]
    banks = Bank.query.filter_by(bmID=current_user.bmID, accounttype="Current")
    form.paidinto.choices = [(bank.bankID, bank.bankname + " - " + bank.accounttype) for bank in banks]
    if form.validate_on_submit():
        new_income = Income(
            bmID=current_user.bmID,
            owner=form.owner.data,
            amount=form.amount.data,
            frequency=form.frequency.data,
            paidinto=form.paidinto.data,
            nextduedate=form.nextduedate.data
        )
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for("view_incomes"))
    return render_template("add-income.html", form=form)


@app.route("/edit-income/<int:income_id>", methods=["GET", "POST"])
def edit_income(income_id):
    income = Income.query.get(income_id)
    edit_form = IncomeForm(
        owner=get_member_name(income.owner),
        amount=income.amount,
        frequency=income.frequency,
        paidinto=get_bank_name(income.paidinto),
        nextduedate=income.nextduedate
    )
    users = User.query.filter_by(bmID=current_user.bmID)
    edit_form.owner.choices = [(user.id, user.firstname) for user in users]
    banks = Bank.query.filter_by(bmID=current_user.bmID, accounttype="Current")
    edit_form.paidinto.choices = [(bank.bankID, bank.bankname + " - " + bank.accounttype) for bank in banks]
    if edit_form.validate_on_submit():
        income.owner = edit_form.owner.data,
        income.amount = edit_form.amount.data,
        income.frequency = edit_form.frequency.data,
        income.paidinto = edit_form.paidinto.data,
        income.nextduedate = edit_form.nextduedate.data
        db.session.commit()
        return redirect(url_for("view_income"))
    return render_template("add-income.html", form=edit_form)


@app.route("/delete-income/<income_id>")
def delete_income(income_id):
    income_to_delete = Income.query.get(income_id)
    db.session.delete(income_to_delete)
    db.session.commit()
    return redirect(url_for("view_incomes"))


# Outgoings
@app.route("/view-outgoings", methods=["GET", "POST"])
def view_outgoings():
    outgoings = Outgoing.query.filter_by(bmID=current_user.bmID)
    variables = Variable.query.filter_by(bmID=current_user.bmID)
    return render_template(
        "outgoings.html",
        outgoings=outgoings,
        variables=variables,
        cat_name=get_category_name,
        sub_cat_name=get_sub_category_name,
        bank_name=get_bank_name
    )


@app.route("/manage-categories", methods=["GET", "POST"])
def manage_categories():
    categories = OutgoingCategory.query.all()
    subcategories = SubCategory.query.all()
    return render_template("categories.html", categories=categories, subcategories=subcategories)


@app.route("/add-sub-category", methods=["GET", "POST"])
def add_sub_category():
    form = SubCategoryForm()
    categories = OutgoingCategory.query.all()
    form.parent.choices = [(category.catID, category.categoryname) for category in categories]
    if form.validate_on_submit():
        new_sub = SubCategory(
            parentcategory=form.parent.data,
            subcategoryname=form.sub_category.data
        )
        db.session.add(new_sub)
        db.session.commit()
        return redirect(url_for('manage_categories'))
    return render_template("add-sub-category.html", form=form)


@app.route("/add-outgoing", methods=["GET", "POST"])
def add_outgoing():
    form = OutgoingForm()
    categories = OutgoingCategory.query.all()
    banks = Bank.query.filter_by(bmID=current_user.bmID)
    form.category.choices = [(category.catID, category.categoryname) for category in categories]
    form.paidfrom.choices = [(bank.bankID, bank.bankname + " - " + bank.accounttype) for bank in banks]
    form.subcategory.choices = [
        (sub_cat.subID, sub_cat.subcategoryname)
        for sub_cat in
        SubCategory.query.filter_by(parentcategory=1).all()]
    if request.method == "POST":
        new_outgoing = Outgoing(
            bmID=current_user.bmID,
            amount=form.amount.data,
            frequency=form.frequency.data,
            nextduedate=form.nextduedate.data,
            category=form.category.data,
            subcategory=form.subcategory.data,
            paidfrom=form.paidfrom.data
        )
        db.session.add(new_outgoing)
        db.session.commit()
        return redirect(url_for("view_outgoings"))
    return render_template("add-outgoing.html", form=form, categories=categories)


@app.route("/add-variable", methods=["GET", "POST"])
def add_variable():
    form = VariableForm()
    categories = OutgoingCategory.query.all()
    form.category.choices = [(category.catID, category.categoryname) for category in categories]
    form.subcategory.choices = [
        (sub_cat.subID, sub_cat.subcategoryname)
        for sub_cat in
        SubCategory.query.filter_by(parentcategory=1).all()]
    if request.method == "POST":
        new_variable = Variable(
            bmID=current_user.bmID,
            amount=form.amount.data,
            frequency=form.frequency.data,
            category=form.category.data,
            subcategory=form.subcategory.data
        )
        db.session.add(new_variable)
        db.session.commit()
        return redirect(url_for("view_outgoings"))
    return render_template("add-variable.html", form=form, categories=categories)


@app.route('/edit-outgoing/<outgoing_id>', methods=["GET", "POST"])
def edit_outgoing(outgoing_id):
    outgoing = Outgoing.query.get(outgoing_id)
    edit_form = OutgoingForm(
        amount=outgoing.amount,
        frequency=outgoing.frequency,
        nextduedate=outgoing.nextduedate,
        paidfrom=outgoing.paidfrom,
        category=outgoing.category,
        subcategory=outgoing.subcategory
    )
    categories = OutgoingCategory.query.all()
    if request.method == "POST":
        outgoing.amount=edit_form.amount.data
        outgoing.frequency=edit_form.frequency.data
        outgoing.nextduedate=edit_form.nextduedate.data
        outgoing.paidfrom=edit_form.paidfrom.data
        outgoing.category=edit_form.category.data
        outgoing.subcategory=edit_form.subcategory.data
        db.session.commit()
        return redirect(url_for("view_outgoings"))
    return render_template("add-outgoing.html", form=edit_form, categories=categories)


@app.route('/edit-variable/<variable_id>', methods=["GET", "POST"])
def edit_variable(variable_id):
    variable = Variable.query.get(variable_id)
    edit_form = VariableForm(
        amount=variable.amount,
        frequency=variable.frequency,
        category=variable.category,
        subcategory=variable.subcategory
    )
    categories = OutgoingCategory.query.all()
    if request.method == "POST":
        variable.amount=edit_form.amount.data
        variable.frequency=edit_form.frequency.data
        variable.category=edit_form.category.data
        variable.subcategory=edit_form.subcategory.data
        db.session.commit()
        return redirect(url_for("view_outgoings"))
    return render_template("add-variable.html", form=edit_form, categories=categories)


@app.route("/delete-outgoing/<outgoing_id>")
def delete_outgoing(outgoing_id):
    outgoing_to_delete = Outgoing.query.get(outgoing_id)
    db.session.delete(outgoing_to_delete)
    db.session.commit()
    return redirect(url_for("view_outgoings"))


@app.route("/delete-variable/<variable_id>")
def delete_variable(variable_id):
    variable_to_delete = Variable.query.get(variable_id)
    db.session.delete(variable_to_delete)
    db.session.commit()
    return redirect(url_for("view_outgoings"))


# Transfers
@app.route("/view-transfers", methods=["GET", "POST"])
def view_transfers():
    transfers = Transfer.query.filter_by(bmID=current_user.bmID)
    banks = Bank.query.filter_by(bmID=current_user.bmID).count()
    return render_template("transfers.html", transfers=transfers, banks=banks, bank_name=get_bank_name)


@app.route("/add-transfer", methods=["GET", "POST"])
def add_transfer():
    form = TransferForm()
    banks = Bank.query.filter_by(bmID=current_user.bmID)
    form.accountfrom.choices = [(bank.bankID, bank.bankname + " - " + bank.accounttype) for bank in banks]
    form.accountto.choices = [(bank.bankID, bank.bankname + " - " + bank.accounttype) for bank in banks]
    if form.validate_on_submit():
        new_transfer = Transfer(
            bmID=current_user.bmID,
            accountfrom=form.accountfrom.data,
            accountto=form.accountto.data,
            amount=form.amount.data,
            frequency=form.frequency.data,
            nextduedate=form.nextduedate.data
        )
        db.session.add(new_transfer)
        db.session.commit()
        return redirect(url_for('view_transfers'))
    return render_template("add-transfer.html", form=form)


@app.route("/edit-transfer/<transfer_id>", methods=["GET", "POST"])
def edit_transfer(transfer_id):
    transfer = Transfer.query.get(transfer_id)
    edit_form = TransferForm(
        paidfrom = transfer.paidfrom,
        paidto = transfer.paidto,
        amount = transfer.amount,
        frequency = transfer.frequency,
        nextduedate = transfer.nextduedate
    )
    if edit_form.validate_on_submit():
        transfer.paidfrom = edit_form.paidfrom.data,
        transfer.paidto = edit_form.paidto.data,
        transfer.amount = edit_form.amount.data,
        transfer.frequency = edit_form.frequency.data,
        transfer.nextduedate = edit_form.nextduedate.data
        db.session.commit()
        return redirect(url_for("view_transfers"))
    return render_template("add-transfer.html", form=edit_form)


@app.route('/delete-transfer/<transfer_id>', methods=["GET", "POST"])
def delete_transfer(transfer_id):
    transfer_to_delete = Transfer.query.get(transfer_id)
    db.session.delete(transfer_to_delete)
    db.session.commit()
    return redirect(url_for('view_transfers'))


# Categories
@app.route("/add-outgoing/<category>")
def sub_category(category):
    sub_categories = SubCategory.query.filter_by(parentcategory=category).all()
    subArray = []
    for cat in sub_categories:
        catObj = {"id": cat.subID, "name": cat.subcategoryname}
        subArray.append(catObj)
    return jsonify({"sub_categories": subArray})


def get_category_name(category_id):
    category = OutgoingCategory.query.get(category_id)
    return category.categoryname


def get_sub_category_name(subcat_id):
    sub_category = SubCategory.query.get(subcat_id)
    return sub_category.subcategoryname


def get_member_name(user_id):
    user = User.query.get(user_id)
    return user.firstname


def get_bank_name(bank_id):
    bank = Bank.query.get(bank_id)
    return bank.bankname + " - " + bank.accounttype


if __name__ == "__main__":
    app.run(debug=True)
