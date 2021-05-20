from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, IntegerField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, NumberRange


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    firstname = StringField("First Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class BudgetStylwForm(FlaskForm):
    type = SelectField("Budget Style", choices=["Weekly", "Monthly"])
    submit = SubmitField("Save")


class MemberForm(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    email = StringField("Email", validators=[Email()])
    submit = SubmitField("Save")


class BankForm(FlaskForm):
    bankname = StringField("Bank name", validators=[DataRequired()])
    acctype = SelectField("Account Type", choices=["Current", "Direct Debit", "Savings"])
    opening_balance = FloatField("Opening Balance", validators=[DataRequired()])
    submit = SubmitField("Save")


class BankEditForm(FlaskForm):
    bankname = StringField("Bank name", validators=[DataRequired()])
    acctype = SelectField("Account Type", choices=["Current", "Direct Debit", "Savings"])
    updated_balance = FloatField('Updated Balance', default=0)
    submit = SubmitField("Save")


class IncomeForm(FlaskForm):
    owner = SelectField("Owner", coerce=int)
    amount = FloatField("Income Amount", validators=[DataRequired()])
    frequency = SelectField("Income Frequency", choices=["Monthly", "Weekly",  "Annually"])
    paidinto = SelectField("Account Paid Into", coerce=int)
    nextduedate = IntegerField("Regular Due Date", validators=[NumberRange(
        min=1,
        max=28,
        message="Please enter a value between 1 and 28")])
    submit = SubmitField("Save")


class OutgoingForm(FlaskForm):
    amount = FloatField("Outgoing Amount", validators=[DataRequired()])
    frequency = SelectField("Outgoing Frequency", choices=["Monthly", "Weekly",  "Annually"])
    nextduedate = IntegerField("Regular Due Date", validators=[NumberRange(
        min=1,
        max=28,
        message="Please enter a value between 1 and 28")])
    paidfrom = SelectField("Account Paid From", coerce=int)
    category = SelectField("Outgoing Category", coerce=int)
    subcategory = SelectField("Sub Category", coerce=int)
    submit = SubmitField("Save")


class VariableForm(FlaskForm):
    amount = FloatField("Budgeted Amount", validators=[DataRequired()])
    frequency = SelectField("Outgoing Frequency", choices=["Daily", "Weekly", "Monthly"])
    category = SelectField("Outgoing Category", coerce=int)
    subcategory = SelectField("Sub Category", coerce=int)
    submit = SubmitField("Save")


class SubCategoryForm(FlaskForm):
    parent = SelectField("Parent Category", coerce=int)
    sub_category = StringField("Sub Category", validators=[DataRequired()])
    submit = SubmitField("Save")


class TransferForm(FlaskForm):
    accountfrom = SelectField("Account Paid From", coerce=int)
    accountto = SelectField("Account Paid To", coerce=int)
    amount = FloatField("Transfer Amount", validators=[DataRequired()])
    frequency = SelectField("Transfer Frequency", choices=["Monthly", "Weekly",  "Annually"])
    nextduedate = IntegerField("Regular Due Date", validators=[NumberRange(
        min=1,
        max=28,
        message="Please enter a value between 1 and 28")])
    submit = SubmitField("Save")


class ForecastForm(FlaskForm):
    name = StringField("Name of the forecast, eg '2 months - normal', '3 months - 5% pay rise'", validators=[DataRequired()])
    project = SelectField("Project budget across a number of months: ", choices=[1, 2, 3, 6, 12, 24])
    vary_income = SelectField("Vary your income across the forecast", choices=["Level", "Increase 3%", "Increase 5%", "Decrease 3%", "Decrease 5%"])
    vary_outgoings = SelectField("Vary your outgoings across the forecast", choices=["Level", "Increase 3%", "Increase 5%", "Decrease 3%", "Decrease 5%"])
    submit = SubmitField("Save")


class ActualSettingForm(FlaskForm):
    setting = SelectField("Start Budget from: ", choices=["Today", "1st of the month"])
    submit = SubmitField("Go")
