from collections import Counter, defaultdict
from decimal import Decimal

from app.models.surgery import SurgeryCase
from app.services.surgery_service import SurgeryService


class SurgeryAnalyticsService:
    """Simple module-level surgery analytics.

    This is not per-surgery insight.
    It prepares the module for future analysis without becoming Finance.
    """

    @staticmethod
    def summarize(surgeries):
        by_status = Counter(surgery.status for surgery in surgeries)
        by_category = Counter(surgery.procedure_category for surgery in surgeries)
        by_month = Counter(surgery.scheduled_at.strftime("%Y-%m") for surgery in surgeries if surgery.scheduled_at)

        total_fee = sum((surgery.fee_amount or Decimal("0")) for surgery in surgeries)
        total_paid = sum((surgery.paid_amount or Decimal("0")) for surgery in surgeries)
        outstanding = total_fee - total_paid

        return {
            "total_count": len(surgeries),
            "by_status": by_status,
            "by_category": by_category,
            "by_month": by_month,
            "total_fee": total_fee,
            "total_paid": total_paid,
            "outstanding": outstanding,
            "category_labels": SurgeryService.CATEGORY_LABELS,
            "status_labels": SurgeryService.STATUS_LABELS,
        }

    @staticmethod
    def summarize_by_date_range(date_from=None, date_to=None):
        surgeries = SurgeryService.list_by_date_range(date_from=date_from, date_to=date_to)
        return SurgeryAnalyticsService.summarize(surgeries)
