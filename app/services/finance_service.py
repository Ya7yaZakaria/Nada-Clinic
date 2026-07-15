from datetime import date
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.finance import FinanceCharge, FinanceExpense, FinancePayment


class FinanceService:
    """Central finance layer for embedded clinic payments and expenses."""

    SERVICE_LABELS = {
        FinanceCharge.SERVICE_CONSULTATION: "كشف",
        FinanceCharge.SERVICE_FOLLOW_UP: "إعادة كشف",
        FinanceCharge.SERVICE_EMERGENCY: "كشف طوارئ",
        FinanceCharge.SERVICE_SURGERY: "عملية",
        FinanceCharge.SERVICE_PROCEDURE: "Procedure",
        FinanceCharge.SERVICE_ULTRASOUND: "Ultrasound",
        FinanceCharge.SERVICE_INVESTIGATION: "Investigation",
        FinanceCharge.SERVICE_OTHER: "Other",
    }

    PAYMENT_METHOD_LABELS = {
        FinancePayment.METHOD_CASH: "Cash",
        FinancePayment.METHOD_INSTAPAY: "Instapay",
        FinancePayment.METHOD_VODAFONE_CASH: "Vodafone Cash",
        FinancePayment.METHOD_CARD: "Card",
        FinancePayment.METHOD_BANK_TRANSFER: "Bank transfer",
        FinancePayment.METHOD_OTHER: "Other",
    }

    EXPENSE_CATEGORY_LABELS = {
        FinanceExpense.CATEGORY_CONSUMABLES: "مستهلكات",
        FinanceExpense.CATEGORY_SALARIES: "مرتبات",
        FinanceExpense.CATEGORY_RENT: "Rent",
        FinanceExpense.CATEGORY_UTILITIES: "Utilities",
        FinanceExpense.CATEGORY_MAINTENANCE: "Maintenance",
        FinanceExpense.CATEGORY_EQUIPMENT: "Equipment",
        FinanceExpense.CATEGORY_MARKETING: "Marketing",
        FinanceExpense.CATEGORY_CLEANING: "Cleaning",
        FinanceExpense.CATEGORY_OTHER: "Other",
    }

    @staticmethod
    def normalize_money(value, default=None):
        if value in ("", None):
            return default
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid money amount.")

    @staticmethod
    def clean(value):
        return (value or "").strip()

    @classmethod
    def payment_method_choices(cls):
        return list(cls.PAYMENT_METHOD_LABELS.items())

    @classmethod
    def service_type_choices(cls):
        return list(cls.SERVICE_LABELS.items())

    @classmethod
    def expense_category_choices(cls):
        return list(cls.EXPENSE_CATEGORY_LABELS.items())

    @classmethod
    def get_payment_method_label(cls, value):
        return cls.PAYMENT_METHOD_LABELS.get(value, value or "—")

    @classmethod
    def get_service_label(cls, value):
        return cls.SERVICE_LABELS.get(value, value or "—")

    @classmethod
    def get_expense_category_label(cls, value):
        return cls.EXPENSE_CATEGORY_LABELS.get(value, value or "—")

    @staticmethod
    def calculate_status(net_amount, paid_amount):
        net = FinanceService.normalize_money(net_amount, Decimal("0.00")) or Decimal("0.00")
        paid = FinanceService.normalize_money(paid_amount, Decimal("0.00")) or Decimal("0.00")

        if net <= 0:
            return FinanceCharge.STATUS_PAID, Decimal("0.00"), paid

        if paid <= 0:
            return FinanceCharge.STATUS_UNPAID, net, Decimal("0.00")

        if paid < net:
            return FinanceCharge.STATUS_PARTIAL, net - paid, paid

        return FinanceCharge.STATUS_PAID, Decimal("0.00"), paid

    @staticmethod
    def validate_payment_method(payment_method, required=False):
        if payment_method in ("", None):
            if required:
                raise ValueError("Payment method is required.")
            return None

        if payment_method not in FinancePayment.VALID_METHODS:
            raise ValueError("Invalid payment method.")

        return payment_method

    @staticmethod
    def validate_service_type(service_type):
        if service_type not in FinanceCharge.VALID_SERVICE_TYPES:
            raise ValueError("Invalid service type.")
        return service_type

    @staticmethod
    def validate_expense_category(category):
        if category not in FinanceExpense.VALID_CATEGORIES:
            raise ValueError("Invalid expense category.")
        return category

    @staticmethod
    def get_charge_for_source(source_type, source_id):
        if not source_type or not source_id:
            return None

        return FinanceCharge.query.filter_by(
            source_type=source_type,
            source_id=source_id,
        ).first()

    @classmethod
    def create_or_update_source_charge(
        cls,
        *,
        patient,
        source_type,
        source_id,
        service_type,
        title,
        gross_amount=None,
        discount_amount=None,
        paid_amount=None,
        payment_method=None,
        service_date=None,
        description=None,
        actor_user=None,
    ):
        if not patient:
            raise ValueError("Patient is required for finance charge.")

        service_type = cls.validate_service_type(service_type)
        gross = cls.normalize_money(gross_amount, None)
        discount = cls.normalize_money(discount_amount, Decimal("0.00")) or Decimal("0.00")
        paid = cls.normalize_money(paid_amount, Decimal("0.00")) or Decimal("0.00")
        payment_method = cls.validate_payment_method(payment_method, required=paid > 0)

        if gross is None:
            return None

        if gross < 0 or discount < 0 or paid < 0:
            raise ValueError("Finance amounts cannot be negative.")

        net = gross - discount
        if net < 0:
            raise ValueError("Discount cannot exceed fee.")

        status, remaining, effective_paid = cls.calculate_status(net, paid)

        charge = cls.get_charge_for_source(source_type, source_id)
        if charge is None:
            charge = FinanceCharge(
                patient=patient,
                source_type=source_type,
                source_id=source_id,
                service_type=service_type,
                created_by_user=actor_user,
            )
            db.session.add(charge)

        charge.title = cls.clean(title) or cls.get_service_label(service_type)
        charge.description = cls.clean(description) or None
        charge.service_type = service_type
        charge.gross_amount = gross
        charge.discount_amount = discount
        charge.net_amount = net
        charge.paid_amount = effective_paid
        charge.remaining_amount = remaining
        charge.status = status
        charge.service_date = service_date or date.today()
        charge.updated_by_user = actor_user

        db.session.flush()

        cls.replace_embedded_payment_snapshot(
            charge=charge,
            amount=effective_paid,
            payment_method=payment_method,
            payment_date=charge.service_date,
            actor_user=actor_user,
            commit=False,
        )

        db.session.commit()
        return charge

    @classmethod
    def replace_embedded_payment_snapshot(
        cls,
        *,
        charge,
        amount,
        payment_method=None,
        payment_date=None,
        actor_user=None,
        commit=True,
    ):
        amount = cls.normalize_money(amount, Decimal("0.00")) or Decimal("0.00")

        for existing in list(charge.payments.all()):
            db.session.delete(existing)

        if amount > 0:
            payment_method = cls.validate_payment_method(payment_method, required=True)
            payment = FinancePayment(
                patient=charge.patient,
                charge=charge,
                payment_date=payment_date or date.today(),
                amount=amount,
                payment_method=payment_method,
                notes="Embedded workflow payment snapshot.",
                created_by_user=actor_user,
            )
            db.session.add(payment)

        if commit:
            db.session.commit()

    @staticmethod
    def cancel_source_charge(source_type, source_id, actor_user=None):
        charge = FinanceService.get_charge_for_source(source_type, source_id)
        if not charge:
            return None

        if charge.paid_amount and charge.paid_amount > 0:
            charge.description = ((charge.description or "") + "\nSource cancelled; payment retained.").strip()
        else:
            charge.status = FinanceCharge.STATUS_CANCELLED
            charge.remaining_amount = Decimal("0.00")

        charge.updated_by_user = actor_user
        db.session.commit()
        return charge

    @staticmethod
    def list_patient_charges(patient):
        return (
            FinanceCharge.query.filter_by(patient_id=patient.id)
            .order_by(FinanceCharge.service_date.desc(), FinanceCharge.id.desc())
            .all()
        )

    @staticmethod
    def list_patient_payments(patient):
        return (
            FinancePayment.query.filter_by(patient_id=patient.id)
            .order_by(FinancePayment.payment_date.desc(), FinancePayment.id.desc())
            .all()
        )

    @staticmethod
    def sum_money(values):
        total = Decimal("0.00")
        for value in values:
            if value is not None:
                total += Decimal(str(value))
        return total

    @classmethod
    def get_patient_finance_summary(cls, patient):
        charges = cls.list_patient_charges(patient)
        active_charges = [charge for charge in charges if charge.status != FinanceCharge.STATUS_CANCELLED]
        return {
            "charges": charges[:8],
            "total_charges": cls.sum_money(charge.net_amount for charge in active_charges),
            "total_paid": cls.sum_money(charge.paid_amount for charge in active_charges),
            "total_remaining": cls.sum_money(charge.remaining_amount for charge in active_charges),
            "unpaid_or_partial": [
                charge
                for charge in active_charges
                if charge.status in {FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL}
            ],
        }

    @classmethod
    def create_expense(
        cls,
        *,
        expense_date,
        category,
        title,
        amount,
        payment_method,
        vendor_or_staff_name=None,
        notes=None,
        actor_user=None,
    ):
        category = cls.validate_expense_category(category)
        amount = cls.normalize_money(amount, Decimal("0.00")) or Decimal("0.00")
        payment_method = cls.validate_payment_method(payment_method, required=True)

        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        title = cls.clean(title)
        if not title:
            raise ValueError("Expense title is required.")

        expense = FinanceExpense(
            expense_date=expense_date or date.today(),
            category=category,
            title=title,
            amount=amount,
            payment_method=payment_method,
            vendor_or_staff_name=cls.clean(vendor_or_staff_name) or None,
            notes=cls.clean(notes) or None,
            created_by_user=actor_user,
        )
        db.session.add(expense)
        db.session.commit()
        return expense

    @classmethod
    def update_expense(
        cls,
        expense,
        *,
        expense_date,
        category,
        title,
        amount,
        payment_method,
        vendor_or_staff_name=None,
        notes=None,
    ):
        if not expense:
            raise ValueError("Expense is required.")

        category = cls.validate_expense_category(category)
        amount = cls.normalize_money(amount, Decimal("0.00")) or Decimal("0.00")
        payment_method = cls.validate_payment_method(payment_method, required=True)

        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        title = cls.clean(title)
        if not title:
            raise ValueError("Expense title is required.")

        expense.expense_date = expense_date or date.today()
        expense.category = category
        expense.title = title
        expense.amount = amount
        expense.payment_method = payment_method
        expense.vendor_or_staff_name = cls.clean(vendor_or_staff_name) or None
        expense.notes = cls.clean(notes) or None
        db.session.commit()
        return expense

    @staticmethod
    def get_expense(expense_uuid):
        if not expense_uuid:
            return None
        return FinanceExpense.query.filter_by(uuid=expense_uuid).first()

    @staticmethod
    def list_expenses(date_from=None, date_to=None, category=None):
        query = FinanceExpense.query
        if date_from:
            query = query.filter(FinanceExpense.expense_date >= date_from)
        if date_to:
            query = query.filter(FinanceExpense.expense_date <= date_to)
        if category:
            query = query.filter(FinanceExpense.category == category)
        return query.order_by(FinanceExpense.expense_date.desc(), FinanceExpense.id.desc()).all()


    @staticmethod
    def _date_range_query(model, column, date_from=None, date_to=None):
        query = model.query
        if date_from:
            query = query.filter(column >= date_from)
        if date_to:
            query = query.filter(column <= date_to)
        return query

    @classmethod
    def _breakdown_by_service(cls, charges):
        rows = {
            key: {
                "key": key,
                "label": label,
                "count": 0,
                "amount": Decimal("0.00"),
                "paid": Decimal("0.00"),
                "remaining": Decimal("0.00"),
                "net": Decimal("0.00"),
            }
            for key, label in cls.SERVICE_LABELS.items()
        }

        for charge in charges:
            key = charge.service_type or FinanceCharge.SERVICE_OTHER
            if key not in rows:
                rows[key] = {
                    "key": key,
                    "label": cls.get_service_label(key),
                    "count": 0,
                    "amount": Decimal("0.00"),
                    "paid": Decimal("0.00"),
                    "remaining": Decimal("0.00"),
                    "net": Decimal("0.00"),
                }

            rows[key]["count"] += 1
            rows[key]["amount"] += Decimal(str(charge.net_amount or 0))
            rows[key]["paid"] += Decimal(str(charge.paid_amount or 0))
            rows[key]["remaining"] += Decimal(str(charge.remaining_amount or 0))
            rows[key]["net"] = rows[key]["paid"]

        return sorted(rows.values(), key=lambda row: (row["paid"], row["amount"]), reverse=True)

    @classmethod
    def _breakdown_by_payment_method(cls, payments):
        rows = {
            key: {
                "key": key,
                "label": label,
                "count": 0,
                "amount": Decimal("0.00"),
                "paid": Decimal("0.00"),
                "remaining": Decimal("0.00"),
                "net": Decimal("0.00"),
            }
            for key, label in cls.PAYMENT_METHOD_LABELS.items()
        }

        for payment in payments:
            key = payment.payment_method or FinancePayment.METHOD_OTHER
            if key not in rows:
                rows[key] = {
                    "key": key,
                    "label": cls.get_payment_method_label(key),
                    "count": 0,
                    "amount": Decimal("0.00"),
                    "paid": Decimal("0.00"),
                    "remaining": Decimal("0.00"),
                    "net": Decimal("0.00"),
                }

            rows[key]["count"] += 1
            rows[key]["amount"] += Decimal(str(payment.amount or 0))
            rows[key]["paid"] = rows[key]["amount"]
            rows[key]["net"] = rows[key]["amount"]

        return sorted(rows.values(), key=lambda row: row["amount"], reverse=True)

    @classmethod
    def _breakdown_by_expense_category(cls, expenses):
        rows = {
            key: {
                "key": key,
                "label": label,
                "count": 0,
                "amount": Decimal("0.00"),
                "paid": Decimal("0.00"),
                "remaining": Decimal("0.00"),
                "net": Decimal("0.00"),
            }
            for key, label in cls.EXPENSE_CATEGORY_LABELS.items()
        }

        for expense in expenses:
            key = expense.category or FinanceExpense.CATEGORY_OTHER
            if key not in rows:
                rows[key] = {
                    "key": key,
                    "label": cls.get_expense_category_label(key),
                    "count": 0,
                    "amount": Decimal("0.00"),
                    "paid": Decimal("0.00"),
                    "remaining": Decimal("0.00"),
                    "net": Decimal("0.00"),
                }

            rows[key]["count"] += 1
            rows[key]["amount"] += Decimal(str(expense.amount or 0))
            rows[key]["net"] = rows[key]["amount"]

        return sorted(rows.values(), key=lambda row: row["amount"], reverse=True)

    @classmethod
    def _daily_rows(cls, charges, expenses):
        rows = {}

        for charge in charges:
            day = charge.service_date
            rows.setdefault(
                day,
                {
                    "date": day,
                    "charges": Decimal("0.00"),
                    "collected": Decimal("0.00"),
                    "remaining": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                    "net": Decimal("0.00"),
                },
            )
            rows[day]["charges"] += Decimal(str(charge.net_amount or 0))
            rows[day]["collected"] += Decimal(str(charge.paid_amount or 0))
            rows[day]["remaining"] += Decimal(str(charge.remaining_amount or 0))

        for expense in expenses:
            day = expense.expense_date
            rows.setdefault(
                day,
                {
                    "date": day,
                    "charges": Decimal("0.00"),
                    "collected": Decimal("0.00"),
                    "remaining": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                    "net": Decimal("0.00"),
                },
            )
            rows[day]["expenses"] += Decimal(str(expense.amount or 0))

        for row in rows.values():
            row["net"] = row["collected"] - row["expenses"]

        return [rows[key] for key in sorted(rows.keys(), reverse=True)]

    @classmethod
    def get_insights_summary(cls, date_from=None, date_to=None):
        charges = (
            cls._date_range_query(FinanceCharge, FinanceCharge.service_date, date_from, date_to)
            .filter(FinanceCharge.status != FinanceCharge.STATUS_CANCELLED)
            .order_by(FinanceCharge.service_date.desc(), FinanceCharge.id.desc())
            .all()
        )
        payments = (
            cls._date_range_query(FinancePayment, FinancePayment.payment_date, date_from, date_to)
            .order_by(FinancePayment.payment_date.desc(), FinancePayment.id.desc())
            .all()
        )
        expenses = (
            cls._date_range_query(FinanceExpense, FinanceExpense.expense_date, date_from, date_to)
            .order_by(FinanceExpense.expense_date.desc(), FinanceExpense.id.desc())
            .all()
        )

        total_charges = cls.sum_money(charge.net_amount for charge in charges)
        total_collected = cls.sum_money(payment.amount for payment in payments)
        total_remaining = cls.sum_money(charge.remaining_amount for charge in charges)
        total_expenses = cls.sum_money(expense.amount for expense in expenses)

        outstanding_charges = [
            charge
            for charge in charges
            if charge.status in {FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL}
        ]

        return {
            "date_from": date_from,
            "date_to": date_to,
            "total_charges": total_charges,
            "total_collected": total_collected,
            "total_remaining": total_remaining,
            "total_expenses": total_expenses,
            "net_profit": total_collected - total_expenses,
            "charge_count": len(charges),
            "payment_count": len(payments),
            "expense_count": len(expenses),
            "service_breakdown": cls._breakdown_by_service(charges),
            "payment_method_breakdown": cls._breakdown_by_payment_method(payments),
            "expense_category_breakdown": cls._breakdown_by_expense_category(expenses),
            "daily_rows": cls._daily_rows(charges, expenses),
            "outstanding_charges": outstanding_charges[:20],
            "recent_charges": charges[:20],
            "recent_expenses": expenses[:20],
        }

    @classmethod
    def get_dashboard_summary(cls, clinic_date=None):
        clinic_date = clinic_date or date.today()
        charges = FinanceCharge.query.filter(
            FinanceCharge.service_date == clinic_date,
            FinanceCharge.status != FinanceCharge.STATUS_CANCELLED,
        ).all()
        expenses = FinanceExpense.query.filter_by(expense_date=clinic_date).all()

        total_revenue = cls.sum_money(charge.paid_amount for charge in charges)
        total_charges = cls.sum_money(charge.net_amount for charge in charges)
        total_remaining = cls.sum_money(charge.remaining_amount for charge in charges)
        total_expenses = cls.sum_money(expense.amount for expense in expenses)

        return {
            "clinic_date": clinic_date,
            "total_charges": total_charges,
            "total_revenue": total_revenue,
            "total_remaining": total_remaining,
            "total_expenses": total_expenses,
            "net": total_revenue - total_expenses,
            "recent_charges": charges[-10:],
            "recent_expenses": expenses[-10:],
        }
