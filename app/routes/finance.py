from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.finance_forms import FinanceExpenseForm
from app.services.finance_service import FinanceService
from app.services.rbac_service import RBACService

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.get("/")
@login_required
@RBACService.require_permission("finance.view")
def index():
    summary = FinanceService.get_dashboard_summary(date.today())
    return render_template(
        "finance/index.html",
        summary=summary,
        FinanceService=FinanceService,
    )



def _parse_date(value, fallback=None):
    if not value:
        return fallback

    try:
        return date.fromisoformat(value)
    except ValueError:
        return fallback


@finance_bp.get("/insights")
@login_required
@RBACService.require_permission("finance.insights")
def insights():
    today = date.today()
    default_from = today - timedelta(days=30)

    date_from = _parse_date(request.args.get("date_from"), default_from)
    date_to = _parse_date(request.args.get("date_to"), today)

    if date_from and date_to and date_from > date_to:
        flash("Invalid date range. Start date must be before end date.", "danger")
        date_from, date_to = default_from, today

    summary = FinanceService.get_insights_summary(date_from=date_from, date_to=date_to)

    return render_template(
        "finance/insights.html",
        summary=summary,
        date_from=date_from,
        date_to=date_to,
        FinanceService=FinanceService,
    )

@finance_bp.get("/expenses")
@login_required
@RBACService.require_permission("finance.view")
def expenses():
    expenses = FinanceService.list_expenses()
    return render_template(
        "finance/expenses.html",
        expenses=expenses,
        FinanceService=FinanceService,
    )


@finance_bp.route("/expenses/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("finance.manage")
def new_expense():
    form = FinanceExpenseForm()
    form.set_choices()

    if form.validate_on_submit():
        try:
            FinanceService.create_expense(
                expense_date=form.expense_date.data,
                category=form.category.data,
                title=form.title.data,
                amount=form.amount.data,
                payment_method=form.payment_method.data,
                vendor_or_staff_name=form.vendor_or_staff_name.data,
                notes=form.notes.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("finance/expense_form.html", form=form, expense=None)

        flash("Expense saved.", "success")
        return redirect(url_for("finance.expenses"))

    return render_template("finance/expense_form.html", form=form, expense=None)


@finance_bp.route("/expenses/<expense_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("finance.manage")
def edit_expense(expense_uuid):
    expense = FinanceService.get_expense(expense_uuid)
    if not expense:
        flash("Expense not found.", "danger")
        return redirect(url_for("finance.expenses"))

    form = FinanceExpenseForm(obj=expense)
    form.set_choices()

    if form.validate_on_submit():
        try:
            FinanceService.update_expense(
                expense,
                expense_date=form.expense_date.data,
                category=form.category.data,
                title=form.title.data,
                amount=form.amount.data,
                payment_method=form.payment_method.data,
                vendor_or_staff_name=form.vendor_or_staff_name.data,
                notes=form.notes.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("finance/expense_form.html", form=form, expense=expense)

        flash("Expense updated.", "success")
        return redirect(url_for("finance.expenses"))

    return render_template("finance/expense_form.html", form=form, expense=expense)
