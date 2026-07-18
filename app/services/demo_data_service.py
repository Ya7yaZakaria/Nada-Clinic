
import calendar
import random
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO

from werkzeug.datastructures import FileStorage

from app.extensions import db
from app.models import (
    Appointment,
    ClinicUltrasoundExam,
    Drug,
    DrugForm,
    DrugRoute,
    ExternalUltrasoundRequest,
    FinanceCharge,
    FinanceExpense,
    FinancePayment,
    InvestigationCategory,
    InvestigationOrder,
    InvestigationResult,
    InvestigationTest,
    Journey,
    Partner,
    PartnerSemenAnalysis,
    Patient,
    PatientDocument,
    Prescription,
    SurgeryCase,
    Visit,
)
from app.services.appointment_service import AppointmentService
from app.services.clinic_ultrasound_service import (
    ClinicUltrasoundService,
)
from app.services.document_service import DocumentService
from app.services.external_ultrasound_service import (
    ExternalUltrasoundService,
)
from app.services.finance_service import FinanceService
from app.services.investigation_service import (
    InvestigationService,
)
from app.services.journey_service import JourneyService
from app.services.partner_semen_analysis_service import (
    PartnerSemenAnalysisService,
)
from app.services.partner_service import PartnerService
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.surgery_service import SurgeryService


class DemoDataService:
    """Generate deterministic five-month clinic trial data."""

    RANDOM_SEED = 20260718

    PATIENT_COUNT = 180
    FIRST_DEMO_MRN = 910001

    HISTORICAL_MONTHS = 4
    FUTURE_MONTHS = 1

    FRIDAY_WEEKDAY = 4

    DAILY_VOLUME = {
        5: 4,
        6: 5,
        0: 6,
        1: 5,
        2: 7,
        3: 3,
    }

    APPOINTMENT_TIMES = (
        time(9, 0),
        time(9, 30),
        time(10, 0),
        time(10, 30),
        time(11, 0),
        time(11, 30),
        time(12, 0),
    )

    FIRST_NAMES_EN = (
        "Sara",
        "Mona",
        "Aya",
        "Mariam",
        "Heba",
        "Nour",
        "Rania",
        "Somaya",
        "Doaa",
        "Noha",
        "Asmaa",
        "Shaimaa",
        "Salma",
        "Hagar",
        "Fatma",
    )

    FIRST_NAMES_AR = (
        "\u0633\u0627\u0631\u0629",
        "\u0645\u0646\u0649",
        "\u0622\u064a\u0629",
        "\u0645\u0631\u064a\u0645",
        "\u0647\u0628\u0629",
        "\u0646\u0648\u0631",
        "\u0631\u0627\u0646\u064a\u0627",
        "\u0633\u0645\u064a\u0629",
        "\u062f\u0639\u0627\u0621",
        "\u0646\u0647\u0649",
        "\u0623\u0633\u0645\u0627\u0621",
        "\u0634\u064a\u0645\u0627\u0621",
        "\u0633\u0644\u0645\u0649",
        "\u0647\u0627\u062c\u0631",
        "\u0641\u0627\u0637\u0645\u0629",
    )

    FAMILY_NAMES_EN = (
        "Ahmed",
        "Mohamed",
        "Mahmoud",
        "Mostafa",
        "Hassan",
        "Khaled",
        "Adel",
        "Samir",
        "Ibrahim",
        "Youssef",
    )

    FAMILY_NAMES_AR = (
        "\u0623\u062d\u0645\u062f",
        "\u0645\u062d\u0645\u062f",
        "\u0645\u062d\u0645\u0648\u062f",
        "\u0645\u0635\u0637\u0641\u0649",
        "\u062d\u0633\u0646",
        "\u062e\u0627\u0644\u062f",
        "\u0639\u0627\u062f\u0644",
        "\u0633\u0645\u064a\u0631",
        "\u0625\u0628\u0631\u0627\u0647\u064a\u0645",
        "\u064a\u0648\u0633\u0641",
    )

    ADDRESSES = (
        ("Cairo", "Nasr City"),
        ("Cairo", "Heliopolis"),
        ("Giza", "Dokki"),
        ("Giza", "Haram"),
        ("Qalyubia", "Banha"),
        ("Gharbia", "Tanta"),
        ("Monufia", "Shebin El Kom"),
    )

    OCCUPATIONS = (
        "Housewife",
        "Teacher",
        "Accountant",
        "Engineer",
        "Pharmacist",
        "Nurse",
        "Employee",
        "Student",
    )

    PAYMENT_METHODS = (
        FinancePayment.METHOD_CASH,
        FinancePayment.METHOD_INSTAPAY,
        FinancePayment.METHOD_VODAFONE_CASH,
        FinancePayment.METHOD_CARD,
        FinancePayment.METHOD_BANK_TRANSFER,
    )

    SURGERY_SCENARIOS = (
        (
            "Cesarean section",
            SurgeryCase.CATEGORY_CESAREAN_SECTION,
            18000,
        ),
        (
            "Diagnostic hysteroscopy",
            SurgeryCase.CATEGORY_HYSTEROSCOPY,
            9000,
        ),
        (
            "Operative hysteroscopy",
            SurgeryCase.CATEGORY_HYSTEROSCOPY,
            14000,
        ),
        (
            "Laparoscopic ovarian cystectomy",
            SurgeryCase.CATEGORY_LAPAROSCOPY,
            28000,
        ),
        (
            "Laparoscopic endometriosis surgery",
            SurgeryCase.CATEGORY_LAPAROSCOPY,
            35000,
        ),
        (
            "Dilation and curettage",
            SurgeryCase.CATEGORY_D_AND_C,
            8500,
        ),
        (
            "Minor gynecology procedure",
            SurgeryCase.CATEGORY_MINOR_PROCEDURE,
            4500,
        ),
        (
            "Vaginal repair",
            SurgeryCase.CATEGORY_VAGINAL_SURGERY,
            22000,
        ),
    )

    @classmethod
    def demo_mrns(cls):
        return tuple(
            range(
                cls.FIRST_DEMO_MRN,
                cls.FIRST_DEMO_MRN + cls.PATIENT_COUNT,
            )
        )

    @staticmethod
    def shift_months(value, months):
        month_index = value.month - 1 + months
        year = value.year + month_index // 12
        month = month_index % 12 + 1

        day = min(
            value.day,
            calendar.monthrange(year, month)[1],
        )

        return date(year, month, day)

    @classmethod
    def period_start(cls):
        return cls.shift_months(
            date.today(),
            -cls.HISTORICAL_MONTHS,
        )

    @classmethod
    def period_end(cls):
        return cls.shift_months(
            date.today(),
            cls.FUTURE_MONTHS,
        )

    @classmethod
    def clinic_dates(cls):
        current = cls.period_start()
        end = cls.period_end()
        result = []

        while current <= end:
            if current.weekday() != cls.FRIDAY_WEEKDAY:
                result.append(current)

            current += timedelta(days=1)

        return result

    @classmethod
    def expected_appointment_count(cls):
        return sum(
            cls.DAILY_VOLUME[clinic_date.weekday()]
            for clinic_date in cls.clinic_dates()
        )

    @classmethod
    def seed(cls):
        existing = Patient.query.filter(
            Patient.medical_file_number.in_(
                cls.demo_mrns()
            )
        ).all()

        if len(existing) == cls.PATIENT_COUNT:
            return {
                "created": False,
                "message": "Demo data already exists.",
            }

        if existing:
            existing_mrns = sorted(
                patient.medical_file_number
                for patient in existing
            )

            raise ValueError(
                "Partial demo dataset exists for MRNs: "
                + ", ".join(str(value) for value in existing_mrns)
                + ". Remove those records before retrying."
            )

        rng = random.Random(cls.RANDOM_SEED)

        patients = cls._create_patients(rng)
        reference_data = cls._ensure_reference_data()

        journeys = cls._create_journeys(
            patients,
            rng,
        )

        appointment_rows = cls._create_appointments(
            patients,
            rng,
        )

        completed_visits = cls._create_visits(
            appointment_rows,
            journeys,
            rng,
        )

        cls._create_partners(
            patients,
            journeys,
            rng,
        )

        cls._create_prescriptions(
            completed_visits,
            reference_data["drug"],
        )

        cls._create_investigations(
            completed_visits,
            reference_data["investigation_test"],
        )

        cls._create_ultrasounds(
            completed_visits,
        )

        cls._create_documents(
            completed_visits,
        )

        cls._create_surgeries(
            patients,
            completed_visits,
            rng,
        )

        cls._create_expenses(rng)

        db.session.commit()

        return {
            "created": True,
            "message": "Five-month demo clinic data created.",
        }

    @classmethod
    def _create_patients(cls, rng):
        patients = []

        for index in range(cls.PATIENT_COUNT):
            first_index = index % len(cls.FIRST_NAMES_EN)
            family_index = (
                index // len(cls.FIRST_NAMES_EN)
            ) % len(cls.FAMILY_NAMES_EN)

            birth_year = rng.randint(1981, 2004)
            birth_month = rng.randint(1, 12)
            birth_day = rng.randint(
                1,
                calendar.monthrange(
                    birth_year,
                    birth_month,
                )[1],
            )

            governorate, city = cls.ADDRESSES[
                index % len(cls.ADDRESSES)
            ]

            patient = PatientService.create_patient(
                medical_file_number=(
                    cls.FIRST_DEMO_MRN + index
                ),
                name_ar=(
                    f"{cls.FIRST_NAMES_AR[first_index]} "
                    f"{cls.FAMILY_NAMES_AR[family_index]} "
                    f"{index + 1:03d}"
                ),
                name_en=(
                    f"{cls.FIRST_NAMES_EN[first_index]} "
                    f"{cls.FAMILY_NAMES_EN[family_index]} "
                    f"Demo {index + 1:03d}"
                ),
                phone_primary=f"01092{index:06d}",
                date_of_birth=date(
                    birth_year,
                    birth_month,
                    birth_day,
                ),
                marital_status=(
                    "married"
                    if index % 10 not in {8, 9}
                    else "single"
                ),
                occupation=cls.OCCUPATIONS[
                    index % len(cls.OCCUPATIONS)
                ],
                governorate=governorate,
                city=city,
                street=f"Demo Street {index + 1}",
            )

            patients.append(patient)

        return patients

    @classmethod
    def _ensure_reference_data(cls):
        drug_form = DrugForm.query.filter_by(
            code="demo_tablet"
        ).first()

        if drug_form is None:
            drug_form = DrugForm(
                code="demo_tablet",
                name_en="Tablet",
                name_ar="\u0623\u0642\u0631\u0627\u0635",
                is_active=True,
                sort_order=900,
            )
            db.session.add(drug_form)

        drug_route = DrugRoute.query.filter_by(
            code="demo_oral"
        ).first()

        if drug_route is None:
            drug_route = DrugRoute(
                code="demo_oral",
                name_en="Oral",
                name_ar="\u0639\u0646 \u0637\u0631\u064a\u0642 \u0627\u0644\u0641\u0645",
                is_active=True,
                sort_order=900,
            )
            db.session.add(drug_route)

        db.session.commit()

        drug = Drug.query.filter_by(
            trade_name="Demo Folic Acid",
            form_id=drug_form.id,
            strength="5 mg",
        ).first()

        if drug is None:
            drug = Drug(
                generic_name="Folic Acid",
                trade_name="Demo Folic Acid",
                strength="5 mg",
                form=drug_form,
                route=drug_route,
                doctor_notes="Generated demo medication.",
                is_active=True,
            )
            db.session.add(drug)

        category = InvestigationCategory.query.filter_by(
            code="demo_hormones"
        ).first()

        if category is None:
            category = InvestigationCategory(
                code="demo_hormones",
                name_en="Demo Hormonal Tests",
                name_ar="\u062a\u062d\u0627\u0644\u064a\u0644 \u0647\u0631\u0645\u0648\u0646\u0627\u062a \u062a\u062c\u0631\u064a\u0628\u064a\u0629",
                description="Generated demo category.",
                is_active=True,
                sort_order=900,
            )
            db.session.add(category)

        db.session.commit()

        investigation_test = InvestigationTest.query.filter_by(
            code="demo_tsh"
        ).first()

        if investigation_test is None:
            investigation_test = InvestigationTest(
                category=category,
                code="demo_tsh",
                name_en="TSH Demo",
                name_ar="\u062a\u062d\u0644\u064a\u0644 TSH \u062a\u062c\u0631\u064a\u0628\u064a",
                default_unit="mIU/L",
                default_reference_range="0.4 - 4.0",
                result_kind=(
                    InvestigationTest.RESULT_KIND_NUMERIC
                ),
                is_active=True,
                sort_order=900,
            )
            db.session.add(investigation_test)

        db.session.commit()

        return {
            "drug": drug,
            "investigation_test": investigation_test,
        }

    @classmethod
    def _create_journeys(cls, patients, rng):
        journeys = {}

        for index, patient in enumerate(patients):
            profile = index % 10

            if profile <= 3:
                journey_type = "pregnancy"
                title = "Pregnancy follow-up"
            elif profile <= 6:
                journey_type = "infertility"
                title = "Infertility treatment"
            else:
                journey_type = "gynecology"
                title = "Gynecology follow-up"

            start_date = cls.period_start() + timedelta(
                days=rng.randint(
                    0,
                    max(
                        1,
                        (date.today() - cls.period_start()).days,
                    ),
                )
            )

            journeys[patient.id] = (
                JourneyService.create_journey(
                    patient=patient,
                    journey_type=journey_type,
                    title=f"Demo {title}",
                    description=(
                        "Generated clinical journey for trial use."
                    ),
                    start_date=start_date.isoformat(),
                )
            )

        return journeys

    @classmethod
    def _select_patient(
        cls,
        patients,
        day_index,
        slot_index,
    ):
        index = (
            day_index * 13
            + slot_index * 31
            + day_index // 5
        ) % len(patients)

        return patients[index]

    @staticmethod
    def _appointment_type(
        appointment_index,
        patient,
    ):
        if appointment_index % 27 == 0:
            return Appointment.TYPE_EMERGENCY

        if patient.appointments.count() == 0:
            return Appointment.TYPE_NEW_CONSULTATION

        return Appointment.TYPE_FOLLOW_UP

    @staticmethod
    def _appointment_fee(appointment_type):
        if appointment_type == Appointment.TYPE_EMERGENCY:
            return 700

        if appointment_type == Appointment.TYPE_NEW_CONSULTATION:
            return 500

        return 300

    @classmethod
    def _payment_data(cls, index, fee):
        pattern = index % 10

        if pattern in {0, 1}:
            return 0, None

        method = cls.PAYMENT_METHODS[
            index % len(cls.PAYMENT_METHODS)
        ]

        if pattern in {2, 3}:
            return int(fee * 0.5), method

        return fee, method

    @staticmethod
    def _past_status(index):
        pattern = index % 20

        if pattern in {16, 17}:
            return Appointment.STATUS_CANCELLED

        if pattern in {18, 19}:
            return Appointment.STATUS_NO_SHOW

        return Appointment.STATUS_COMPLETED

    @staticmethod
    def _today_status(slot_index):
        statuses = (
            Appointment.STATUS_COMPLETED,
            Appointment.STATUS_ARRIVED,
            Appointment.STATUS_BOOKED,
            Appointment.STATUS_CANCELLED,
            Appointment.STATUS_NO_SHOW,
            Appointment.STATUS_ARRIVED,
            Appointment.STATUS_BOOKED,
        )

        return statuses[slot_index % len(statuses)]

    @classmethod
    def _create_appointments(cls, patients, rng):
        rows = []
        today = date.today()
        appointment_index = 0

        for day_index, clinic_date in enumerate(
            cls.clinic_dates()
        ):
            daily_volume = cls.DAILY_VOLUME[
                clinic_date.weekday()
            ]

            for slot_index in range(daily_volume):
                patient = cls._select_patient(
                    patients,
                    day_index,
                    slot_index,
                )

                appointment_type = cls._appointment_type(
                    appointment_index,
                    patient,
                )

                if clinic_date < today:
                    status = cls._past_status(
                        appointment_index
                    )
                elif clinic_date == today:
                    status = cls._today_status(
                        slot_index
                    )
                else:
                    status = Appointment.STATUS_BOOKED

                fee = None
                paid = None
                method = None

                if status in {
                    Appointment.STATUS_COMPLETED,
                    Appointment.STATUS_ARRIVED,
                }:
                    fee = cls._appointment_fee(
                        appointment_type
                    )
                    paid, method = cls._payment_data(
                        appointment_index,
                        fee,
                    )

                source = (
                    Appointment.SOURCE_PHONE,
                    Appointment.SOURCE_WHATSAPP,
                    Appointment.SOURCE_CLINIC,
                )[appointment_index % 3]

                if appointment_type == Appointment.TYPE_EMERGENCY:
                    source = (
                        Appointment.SOURCE_EMERGENCY_UNSCHEDULED
                    )

                appointment = (
                    AppointmentService.create_appointment(
                        patient_id=patient.id,
                        appointment_date=clinic_date,
                        appointment_time=(
                            cls.APPOINTMENT_TIMES[
                                slot_index
                                % len(cls.APPOINTMENT_TIMES)
                            ]
                        ),
                        duration_minutes=(
                            30
                            if appointment_type
                            == Appointment.TYPE_NEW_CONSULTATION
                            else 20
                        ),
                        appointment_type=appointment_type,
                        status=status,
                        source=source,
                        notes=(
                            "Generated five-month clinic activity."
                        ),
                        fee_amount=fee,
                        paid_amount=paid,
                        payment_method=method,
                    )
                )

                event_datetime = datetime.combine(
                    clinic_date,
                    appointment.appointment_time
                    or time(9, 0),
                    tzinfo=timezone.utc,
                )

                appointment.created_at = (
                    event_datetime - timedelta(days=2)
                )
                appointment.updated_at = event_datetime

                if status == Appointment.STATUS_COMPLETED:
                    appointment.completed_at = event_datetime
                elif status == Appointment.STATUS_ARRIVED:
                    appointment.arrived_at = event_datetime
                elif status == Appointment.STATUS_CANCELLED:
                    appointment.cancelled_at = event_datetime
                    appointment.cancel_reason = (
                        "Patient requested cancellation."
                    )
                elif status == Appointment.STATUS_NO_SHOW:
                    appointment.no_show_at = event_datetime

                rows.append(
                    {
                        "appointment": appointment,
                        "patient": patient,
                        "date_time": event_datetime,
                        "status": status,
                        "type": appointment_type,
                    }
                )

                appointment_index += 1

        db.session.commit()
        return rows

    @staticmethod
    def _visit_profile(journey):
        if journey.journey_type == "pregnancy":
            return {
                "visit_type": "obs",
                "chief_complaint": (
                    "Routine antenatal follow-up."
                ),
                "history": "No warning symptoms reported.",
                "examination": (
                    "General condition stable."
                ),
                "assessment": (
                    "Pregnancy progressing under follow-up."
                ),
                "plan": (
                    "Continue routine antenatal care."
                ),
            }

        if journey.journey_type == "infertility":
            return {
                "visit_type": "infertility",
                "chief_complaint": (
                    "Infertility follow-up."
                ),
                "history": (
                    "Ongoing fertility assessment."
                ),
                "examination": (
                    "Clinical assessment documented."
                ),
                "assessment": (
                    "Infertility workup or treatment follow-up."
                ),
                "plan": (
                    "Continue investigation and cycle plan."
                ),
            }

        return {
            "visit_type": "gyn",
            "chief_complaint": (
                "Gynecology complaint follow-up."
            ),
            "history": (
                "Symptoms reviewed during clinic visit."
            ),
            "examination": (
                "Gynecology examination documented."
            ),
            "assessment": (
                "Gynecology condition under follow-up."
            ),
            "plan": (
                "Medical treatment and follow-up."
            ),
        }

    @classmethod
    def _create_visits(
        cls,
        appointment_rows,
        journeys,
        rng,
    ):
        visits = []

        for index, row in enumerate(appointment_rows):
            if row["status"] != Appointment.STATUS_COMPLETED:
                continue

            patient = row["patient"]
            journey = journeys[patient.id]
            profile = cls._visit_profile(journey)

            follow_up_date = None

            if index % 4 == 0:
                follow_up_date = (
                    row["date_time"].date()
                    + timedelta(days=14)
                )

            visit = Visit(
                patient=patient,
                journey=journey,
                visit_type=profile["visit_type"],
                status="completed",
                visit_date=row["date_time"],
                started_at=row["date_time"],
                completed_at=(
                    row["date_time"]
                    + timedelta(minutes=20)
                ),
                chief_complaint=profile[
                    "chief_complaint"
                ],
                history=profile["history"],
                examination=profile["examination"],
                assessment=profile["assessment"],
                plan=profile["plan"],
                follow_up_date=follow_up_date,
                is_locked=True,
                created_at=row["date_time"],
                updated_at=row["date_time"],
            )

            db.session.add(visit)
            visits.append(visit)

        db.session.commit()
        return visits

    @classmethod
    def _create_partners(
        cls,
        patients,
        journeys,
        rng,
    ):
        candidates = [
            patient
            for patient in patients
            if (
                journeys[patient.id].journey_type
                == "infertility"
                and patient.marital_status == "married"
            )
        ]

        for index, patient in enumerate(
            candidates[:36]
        ):
            partner = PartnerService.create_partner(
                patient=patient,
                name=f"Demo Partner {index + 1:02d}",
                phone=f"01093{index:06d}",
                age_years=rng.randint(28, 48),
                occupation=(
                    "Engineer"
                    if index % 2 == 0
                    else "Employee"
                ),
                previous_children=(
                    "None"
                    if index % 3
                    else "One previous child"
                ),
                fertility_notes=(
                    "Partner included in infertility assessment."
                ),
                medical_notes=(
                    "No major chronic illness reported."
                ),
                follow_up_note=(
                    "Review semen analysis and treatment plan."
                ),
                follow_up_date=(
                    date.today() + timedelta(days=10)
                ),
            )

            if index % 2 == 0:
                PartnerSemenAnalysisService.create_analysis(
                    partner=partner,
                    analysis_date=(
                        date.today()
                        - timedelta(days=index + 7)
                    ),
                    notes=(
                        "Generated semen analysis review record."
                    ),
                )

    @classmethod
    def _create_prescriptions(cls, visits, drug):
        for index, visit in enumerate(visits):
            if index % 6 != 0:
                continue

            prescription = (
                PrescriptionService.create_prescription(
                    visit=visit,
                    notes=(
                        "Generated treatment prescription."
                    ),
                )
            )

            PrescriptionService.add_item(
                prescription=prescription,
                drug=drug,
                dose="5 mg",
                frequency="Once daily",
                duration="30 days",
                instructions_ar=(
                    "\u0642\u0631\u0635 \u0648\u0627\u062d\u062f "
                    "\u0645\u0631\u0629 \u064a\u0648\u0645\u064a\u0627"
                ),
            )

    @classmethod
    def _create_investigations(
        cls,
        visits,
        investigation_test,
    ):
        selected = [
            visit
            for index, visit in enumerate(visits)
            if index % 5 == 0
        ]

        for index, visit in enumerate(selected):
            order = InvestigationService.create_order(
                patient=visit.patient,
                ordered_visit=visit,
                journey=visit.journey,
                priority=(
                    InvestigationOrder.PRIORITY_IMPORTANT
                    if index % 8 == 0
                    else InvestigationOrder.PRIORITY_ROUTINE
                ),
                order_notes=(
                    "Generated investigation request."
                ),
            )

            item = InvestigationService.add_order_item(
                order=order,
                test=investigation_test,
                item_notes="Generated TSH request.",
            )

            if index % 4 != 0:
                value = (
                    "5.6"
                    if index % 9 == 0
                    else "2.1"
                )

                flag = (
                    InvestigationResult.FLAG_HIGH
                    if value == "5.6"
                    else InvestigationResult.FLAG_NORMAL
                )

                InvestigationService.enter_result_for_order_item(
                    order_item=item,
                    result_date=visit.visit_date.date(),
                    result_visit=visit,
                    lab_name="Demo Laboratory",
                    result_value=value,
                    unit="mIU/L",
                    reference_range="0.4 - 4.0",
                    doctor_comment=(
                        "High result requires review."
                        if flag
                        == InvestigationResult.FLAG_HIGH
                        else "Within normal range."
                    ),
                    abnormal_flag=flag,
                )

    @classmethod
    def _create_ultrasounds(cls, visits):
        for index, visit in enumerate(visits):
            if index % 7 != 0:
                continue

            if (
                visit.journey
                and visit.journey.journey_type
                == "pregnancy"
            ):
                ClinicUltrasoundService.create_exam(
                    visit=visit,
                    exam_type=(
                        ClinicUltrasoundExam.EXAM_TYPE_OBS
                    ),
                    exam_route=(
                        ClinicUltrasoundExam
                        .ROUTE_TRANSABDOMINAL
                    ),
                    findings_json={
                        "fetal_heart_activity": "present",
                        "growth": "consistent with dates",
                    },
                    findings_text=(
                        "Single viable intrauterine pregnancy."
                    ),
                    impression=(
                        "Viable pregnancy under follow-up."
                    ),
                )
            elif (
                visit.journey
                and visit.journey.journey_type
                == "infertility"
            ):
                ClinicUltrasoundService.create_exam(
                    visit=visit,
                    exam_type=(
                        ClinicUltrasoundExam.EXAM_TYPE_OI_TI
                    ),
                    exam_route=(
                        ClinicUltrasoundExam
                        .ROUTE_TRANSVAGINAL
                    ),
                    findings_json={
                        "lead_follicle": "18 mm",
                        "endometrium": "8 mm",
                    },
                    findings_text=(
                        "Follicular monitoring examination."
                    ),
                    impression=(
                        "Mature follicle with suitable endometrium."
                    ),
                )
            else:
                ExternalUltrasoundService.create_direct_result(
                    visit=visit,
                    result_note=(
                        "Generated external pelvic ultrasound result."
                    ),
                    categories=["pelvic"],
                    modalities=["ultrasound"],
                )

    @classmethod
    def _create_documents(cls, visits):
        for index, visit in enumerate(visits):
            if index % 18 != 0:
                continue

            file_storage = FileStorage(
                stream=BytesIO(
                    (
                        "Generated patient document for "
                        "five-month demo data.\n"
                    ).encode("utf-8")
                ),
                filename=(
                    f"demo_patient_document_{index:03d}.txt"
                ),
                content_type="text/plain",
            )

            DocumentService.save_uploaded_file(
                patient=visit.patient,
                visit=visit,
                file_storage=file_storage,
                document_type=PatientDocument.TYPE_OTHER,
                title="Generated patient document",
                description=(
                    "Created by flask seed-demo."
                ),
            )

    @classmethod
    def _create_surgeries(
        cls,
        patients,
        visits,
        rng,
    ):
        today = date.today()
        visit_by_patient = {}

        for visit in visits:
            visit_by_patient.setdefault(
                visit.patient_id,
                visit,
            )

        surgery_count = 28

        for index in range(surgery_count):
            patient = patients[
                (index * 17 + 9) % len(patients)
            ]

            source_visit = visit_by_patient.get(
                patient.id
            )

            procedure_name, category, base_fee = (
                cls.SURGERY_SCENARIOS[
                    index % len(cls.SURGERY_SCENARIOS)
                ]
            )

            if index < 20:
                surgery_date = (
                    cls.period_start()
                    + timedelta(days=7 + index * 5)
                )

                if surgery_date >= today:
                    surgery_date = (
                        today
                        - timedelta(days=index + 2)
                    )
            else:
                surgery_date = (
                    today
                    + timedelta(days=4 + (index - 20) * 3)
                )

            scheduled_at = datetime.combine(
                surgery_date,
                time(14, 0),
                tzinfo=timezone.utc,
            )

            fee = int(
                base_fee
                * (
                    0.9
                    + (index % 3) * 0.1
                )
            )

            if index % 5 == 0:
                paid = 0
                payment_status = (
                    SurgeryCase.PAYMENT_UNPAID
                )
                payment_method = None
            elif index % 4 == 0:
                paid = int(fee * 0.5)
                payment_status = (
                    SurgeryCase.PAYMENT_PARTIAL
                )
                payment_method = (
                    FinancePayment.METHOD_INSTAPAY
                )
            else:
                paid = fee
                payment_status = (
                    SurgeryCase.PAYMENT_PAID
                )
                payment_method = (
                    FinancePayment.METHOD_CASH
                    if index % 2 == 0
                    else FinancePayment
                    .METHOD_BANK_TRANSFER
                )

            surgery = SurgeryService.create_surgery(
                patient=patient,
                source_visit=source_visit,
                procedure_name=procedure_name,
                procedure_category=category,
                scheduled_at=scheduled_at,
                location="Demo Hospital",
                priority=(
                    SurgeryCase.PRIORITY_URGENT
                    if index % 9 == 0
                    else SurgeryCase.PRIORITY_ROUTINE
                ),
                pre_op_note=(
                    "Generated preoperative assessment."
                ),
                surgery_note=(
                    "Generated surgery planning record."
                ),
                fee_amount=fee,
                paid_amount=paid,
                payment_status=payment_status,
                payment_method=payment_method,
            )

            if surgery_date < today:
                if index % 11 == 0:
                    SurgeryService.cancel_surgery(
                        surgery,
                        cancel_reason=(
                            "Patient postponed surgery indefinitely."
                        ),
                    )
                elif index % 7 == 0:
                    SurgeryService.postpone_surgery(
                        surgery,
                        new_scheduled_at=(
                            scheduled_at
                            + timedelta(days=21)
                        ),
                        postponed_reason=(
                            "Medical optimization required."
                        ),
                    )
                else:
                    SurgeryService.complete_surgery(
                        surgery,
                        completed_at=(
                            scheduled_at
                            + timedelta(hours=2)
                        ),
                        operative_findings=(
                            "Expected operative findings."
                        ),
                        operative_details=(
                            "Procedure completed as planned."
                        ),
                        complications="No complications.",
                        post_op_plan=(
                            "Routine postoperative follow-up."
                        ),
                        fee_amount=fee,
                        paid_amount=paid,
                        payment_status=payment_status,
                        payment_method=payment_method,
                    )

    @classmethod
    def _create_expenses(cls, rng):
        monthly_dates = []
        current = cls.period_start().replace(day=1)
        end = cls.period_end().replace(day=1)

        while current <= end:
            monthly_dates.append(current)
            current = cls.shift_months(current, 1)

        recurring = (
            (
                FinanceExpense.CATEGORY_RENT,
                "Clinic rent",
                12000,
                FinancePayment.METHOD_BANK_TRANSFER,
            ),
            (
                FinanceExpense.CATEGORY_SALARIES,
                "Staff salaries",
                18000,
                FinancePayment.METHOD_BANK_TRANSFER,
            ),
            (
                FinanceExpense.CATEGORY_UTILITIES,
                "Electricity and utilities",
                2500,
                FinancePayment.METHOD_CASH,
            ),
            (
                FinanceExpense.CATEGORY_CONSUMABLES,
                "Medical consumables",
                4200,
                FinancePayment.METHOD_CASH,
            ),
            (
                FinanceExpense.CATEGORY_CLEANING,
                "Cleaning services",
                1800,
                FinancePayment.METHOD_CASH,
            ),
        )

        for month_index, month_date in enumerate(
            monthly_dates
        ):
            for item_index, (
                category,
                title,
                base_amount,
                method,
            ) in enumerate(recurring):
                variation = 1 + (
                    ((month_index + item_index) % 3) - 1
                ) * 0.08

                FinanceService.create_expense(
                    expense_date=(
                        month_date
                        + timedelta(days=1 + item_index * 4)
                    ),
                    category=category,
                    title=title,
                    amount=round(
                        base_amount * variation,
                        2,
                    ),
                    payment_method=method,
                    vendor_or_staff_name="Demo Vendor",
                    notes=(
                        "Generated recurring clinic expense."
                    ),
                )

            if month_index % 2 == 0:
                FinanceService.create_expense(
                    expense_date=(
                        month_date + timedelta(days=18)
                    ),
                    category=(
                        FinanceExpense
                        .CATEGORY_MAINTENANCE
                    ),
                    title="Equipment maintenance",
                    amount=3500 + month_index * 250,
                    payment_method=(
                        FinancePayment.METHOD_CASH
                    ),
                    vendor_or_staff_name=(
                        "Demo Maintenance"
                    ),
                    notes=(
                        "Generated maintenance expense."
                    ),
                )

    @classmethod
    def summary(cls):
        demo_filter = Patient.medical_file_number.in_(
            cls.demo_mrns()
        )

        patients = Patient.query.filter(
            demo_filter
        ).count()

        appointments = (
            Appointment.query
            .join(
                Patient,
                Appointment.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        visits = (
            Visit.query
            .join(
                Patient,
                Visit.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        journeys = (
            Journey.query
            .join(
                Patient,
                Journey.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        partners = (
            Partner.query
            .join(
                Patient,
                Partner.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        prescriptions = (
            Prescription.query
            .join(
                Patient,
                Prescription.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        investigation_results = (
            InvestigationResult.query
            .join(
                Patient,
                InvestigationResult.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        clinic_ultrasounds = (
            ClinicUltrasoundExam.query
            .join(
                Patient,
                ClinicUltrasoundExam.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        external_ultrasounds = (
            ExternalUltrasoundRequest.query
            .join(
                Patient,
                ExternalUltrasoundRequest.patient_id
                == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        documents = (
            PatientDocument.query
            .join(
                Patient,
                PatientDocument.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        surgeries = (
            SurgeryCase.query
            .join(
                Patient,
                SurgeryCase.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        finance_charges = (
            FinanceCharge.query
            .join(
                Patient,
                FinanceCharge.patient_id == Patient.id,
            )
            .filter(demo_filter)
            .count()
        )

        return {
            "period_start": cls.period_start(),
            "period_end": cls.period_end(),
            "patients": patients,
            "appointments": appointments,
            "visits": visits,
            "journeys": journeys,
            "partners": partners,
            "prescriptions": prescriptions,
            "investigation_results": investigation_results,
            "clinic_ultrasounds": clinic_ultrasounds,
            "external_ultrasounds": external_ultrasounds,
            "documents": documents,
            "surgeries": surgeries,
            "finance_charges": finance_charges,
            "expenses": FinanceExpense.query.count(),
        }
