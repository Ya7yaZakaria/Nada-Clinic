from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.services.finance_service import FinanceService


class FinanceExpenseForm(FlaskForm):
    expense_date = DateField("Date", validators=[DataRequired()])
    category = SelectField("Category", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(max=180)])
    amount = DecimalField("Amount", places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    payment_method = SelectField("Payment method", validators=[DataRequired()])
    vendor_or_staff_name = StringField("Vendor / Staff", validators=[Optional(), Length(max=180)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save expense")

    def set_choices(self):
        self.category.choices = FinanceService.expense_category_choices()
        self.payment_method.choices = FinanceService.payment_method_choices()
