

Project Direction

Nada Clinic System should be built as a lightweight, fast, AI-ready Clinical Operating System for Women’s Health, not as a heavy ERP or React-heavy dashboard.

Frozen Stack

Backend:

Flask

SQLAlchemy

Alembic

PostgreSQL-ready

  

Frontend:

HTML5

Bootstrap 5

HTMX

Alpine.js

  

Auth:

Flask-Login

Simple RBAC

  

Foundation:

Audit foundation

Local file storage

Print engine

PWA/mobile-ready shell

AI-ready architecture

  

Stage 0 — Project Preparation

Goal

Prepare the project professionally before writing feature code.

Scope

Create the repository foundation, project structure, environment setup, and development workflow.

Deliverables

Flask project skeleton

Virtual environment

Requirements file

Environment config

App factory

Blueprint structure

Base templates

Static assets

Migration setup

Testing setup

README

CHANGELOG

Main Work

Create Flask app factory.

Create config system: development, testing, production.

Initialize SQLAlchemy.

Initialize Alembic.

Initialize Flask-Login.

Create base layout.

Create error pages.

Create health check route.

Create initial test structure.

Suggested Sprints

Sprint 0.1 — Repository Foundation

Goal:

Create clean project structure.

  

Files:

app/__init__.py

app/config.py

app/extensions.py

app/routes/

app/models/

app/services/

app/templates/

app/static/

tests/

migrations/

  

Acceptance:

Application starts.

Health route works.

Tests can run.

Sprint 0.2 — UI Shell Foundation

Goal:

Create global layout.

  

Includes:

Bootstrap 5

HTMX

Alpine.js

Sidebar

Top nav

Base template

Mobile shell

PWA placeholders

  

Acceptance:

Home page renders with final shell.

Sidebar works.

Mobile layout does not break.

  

Stage 1 — Core System Foundation

Goal

Build the minimum secure application foundation.

Scope

Authentication, users, roles, permissions, audit foundation, and settings foundation.

Deliverables

Users

Roles

Permissions

Login/logout

RBAC helpers

Admin user seed

Audit log foundation

Settings table

Base admin area

Main Work

User model.

Role model.

Permission model.

Login flow.

Password hashing.

Protected routes.

RBAC decorator/helper.

AuditLog model.

Settings model.

Admin-only access.

Suggested Sprints

Sprint 1.1 — Auth

Goal:

Users can login/logout securely.

  

Includes:

User model

Password hash

Login route

Logout route

Session protection

Sprint 1.2 — RBAC

Goal:

Separate Doctor, Reception, Admin.

  

Includes:

Role model

Permission model

Permission checks

Access-denied page

Sprint 1.3 — Audit + Settings Foundation

Goal:

Prepare audit and configuration.

  

Includes:

AuditLog table

Settings table

Basic settings page

Audit helper

Acceptance Criteria

Doctor can access clinical pages.

Reception cannot access clinical notes.

Admin can manage basic settings.

Sensitive actions can create audit logs.

  

Stage 2 — Patient Core Foundation

Goal

Build the patient-centered heart of the system.

Scope

Patients, file numbers, patient search, Patient Workspace shell.

Deliverables

Patient model

Patient CRUD

Medical file number

Editable MRN by Admin

Patient search

Patient Workspace

Patient Header

Clinical Snapshot placeholder

Recent patients

Suggested Sprints

Sprint 2.1 — Patient Model & Migration

Goal:

Create patient database foundation.

  

Includes:

Patient table

UUID internal ID

Medical file number

Demographics

Phone

DOB

Admin MRN editing audit

Sprint 2.2 — Patient CRUD

Goal:

Create, edit, view patients.

  

Routes:

GET /patients

GET /patients/new

POST /patients

GET /patients/<id>

POST /patients/<id>/edit

Sprint 2.3 — Patient Search

Goal:

Fast search by name, file number, phone.

  

Includes:

Global search box

HTMX search results

Patient result cards

Sprint 2.4 — Patient Workspace v1

Goal:

Open patient and see core identity.

  

Includes:

Patient Header

Demographics

File number

Last visit placeholder

Clinical snapshot placeholder

Quick actions placeholder

Acceptance Criteria

Patient can be registered in under 1 minute.

Patient can be found by name/file/phone.

Patient Workspace opens quickly.

File number can be changed only by Admin with audit.

  

Stage 3 — Clinical Backbone

Goal

Build the clinical structure: Journey + Visit.

Scope

Journey module, Visit module, structured clinical note, timeline foundation.

Deliverables

Journey model

Visit model

Clinical note fields inside Visit

Optional Journey for Visit

New Visit workflow

Finish Visit workflow

Unassigned visit warning

Timeline foundation

Suggested Sprints

Sprint 3.1 — Journey Module

Goal:

Create clinical context.

  

Includes:

Pregnancy

Gynecology

Infertility

Active/closed journey

Optional partner link later

Sprint 3.2 — Visit Module

Goal:

Create clinical encounter.

  

Includes:

Visit type

Status: Open / Completed / Incomplete

Chief complaint

History

Examination

Assessment

Plan

Follow-up

Sprint 3.3 — Visit Workflow

Goal:

Doctor can start and finish visits.

  

Includes:

New Visit button

Auto-save or save draft

Finish Visit confirmation

Completed Visit edit requires reason

Sprint 3.4 — Timeline Foundation

Goal:

Show patient story from visits/journeys.

  

Includes:

Generated timeline

Visit events

Journey events

Filters later

Acceptance Criteria

Patient can have Visit without Journey.

System warns about unassigned visits.

Doctor can link visit to journey later.

Completed visit updates Last Visit and Clinical Snapshot.

  

Stage 4 — Appointment & Today’s Clinic

Goal

Make daily clinic workflow usable.

Scope

Appointments, arrival, today queue, previous clinic days.

Deliverables

Appointment model

Appointment CRUD

Today’s Clinic

Arrival status

Completed status

Cancelled status

Previous Days Clinic

Suggested Sprints

Sprint 4.1 — Appointment Database

Goal:

Book appointments.

  

Statuses:

Booked

Arrived

Cancelled

Completed

Sprint 4.2 — Reception Booking

Goal:

Reception can book and check-in patients.

  

Includes:

Book appointment

Reschedule

Cancel

Mark arrived

Sprint 4.3 — Today’s Clinic

Goal:

Doctor sees live clinic list.

  

Includes:

Waiting list

Patient preview

Open Patient Workspace

Open Last Visit

Pending flags placeholder

Sprint 4.4 — Previous Days Clinic

Goal:

Review previous clinic days and unfinished work.

Acceptance Criteria

Reception can check-in patient in one click.

Doctor can open next patient quickly.

Appointment does not automatically create visit.

Completed visit can mark appointment completed.

  

Stage 5 — Prescription + Printing Foundation

Goal

Create printable prescriptions and shared print engine.

Scope

Prescription module, prescription items, presets, drug database foundation, print templates.

Deliverables

Drug database

Trade names

Prescription model

Prescription items

Prescription presets

Prescription print

Shared print layout

Suggested Sprints

Sprint 5.1 — Drug Database Foundation

Goal:

Store drugs used in clinic.

  

Includes:

Generic name

Trade name

Form

Strength

Pregnancy/lactation notes placeholder

Sprint 5.2 — Prescription Module

Goal:

Create prescription inside Visit.

  

Includes:

Prescription item

Free text medication line

Reuse previous prescription

Sprint 5.3 — Prescription Presets

Goal:

Doctor can create reusable prescription groups.

Sprint 5.4 — Print Engine v1

Goal:

Print prescription professionally.

  

Includes:

Clinic header

Doctor name

Patient name

Date

Medication lines

Instructions

Signature area

Acceptance Criteria

Doctor can create prescription inside visit.

Prescription can be printed.

Reception cannot edit medication content.

Drug database can grow over time.

  

Stage 6 — Investigations Module

Goal

Order, track, upload, and review investigations.

Scope

Investigation orders, items, results, presets, printable investigation request.

Deliverables

Investigation order

Investigation item

Investigation result

Investigation presets

Pending results

Result review

External report upload

Investigation print request

Suggested Sprints

Sprint 6.1 — Investigation Orders

Goal:

Order individual tests from Visit.

Sprint 6.2 — Investigation Presets

Goal:

Create reusable panels.

  

Examples:

First trimester labs

Infertility workup

Pre-op labs

Sprint 6.3 — Result Entry & Upload

Goal:

Enter or upload external results.

Sprint 6.4 — Result Review

Goal:

Doctor reviews results.

  

Includes:

Reviewed status

Abnormal flag

Pending results notification

Acceptance Criteria

Doctor can order one test or preset.

Pending labs appear in Patient Workspace.

External lab PDFs/images can be uploaded.

Reviewed results update patient timeline.

  

Stage 7 — Documents & Storage

Goal

Create safe patient file storage.

Scope

Local storage, documents, links, upload, preview, download.

Deliverables

Document model

Document upload

Document links

Local storage structure by patient UUID

PDF/image support

SVG sketch support foundation

Suggested Sprints

Sprint 7.1 — Storage Foundation

Goal:

Store files locally outside database.

  

Path:

uploads/patients/{patient_uuid}/...

Sprint 7.2 — Documents Module

Goal:

Upload and view patient documents.

Sprint 7.3 — Document Linking

Goal:

Link one document to multiple objects.

Sprint 7.4 — Sketch Foundation

Goal:

Simple SVG sketch box for ultrasound/visit future use.

Acceptance Criteria

Files are not stored in PostgreSQL.

Every file belongs to Patient.

Document can link to Visit/Surgery/Ultrasound/Investigation.

Original files are preserved.

  

Stage 8 — Ultrasound Module

Goal

Make ultrasound a first-class clinical event.

Scope

In-clinic ultrasound, external ultrasound, measurements, media, sketch.

Deliverables

Ultrasound study

Source: In-clinic / External / Imported

Measurements

Images

Sketch SVG

External report link

Comparison foundation

Suggested Sprints

Sprint 8.1 — Ultrasound Study

Goal:

Create ultrasound record inside Visit.

Sprint 8.2 — Measurements

Goal:

Store structured measurements.

Sprint 8.3 — External Ultrasound

Goal:

Record report from external imaging center.

Sprint 8.4 — Sketch & Media

Goal:

Add SVG sketch and upload images.

Acceptance Criteria

Ultrasound belongs to Patient.

Usually linked to Visit.

Can be external.

Can include sketch.

Appears in timeline.

  

Stage 9 — Surgery Module

Goal

Create Surgical Command Center.

Scope

Surgery calendar, surgery records, operation note, histopathology, follow-up.

Deliverables

Surgery model

Surgery calendar

Operation note inside surgery

Pre-op checklist foundation

Histopathology tracking

Surgery documents

Surgery finance link later

Suggested Sprints

Sprint 9.1 — Surgery Records

Goal:

Schedule and view surgeries.

Sprint 9.2 — Surgery Calendar

Goal:

See upcoming and completed surgeries.

Sprint 9.3 — Operation Note

Goal:

Create draft/finalized operation note.

Sprint 9.4 — Histopathology

Goal:

Track pathology pending/received/reviewed.

Acceptance Criteria

Surgery must link to Patient.

Visit link is optional.

Operation note can remain draft.

Histopathology can generate notifications.

Surgery appears in timeline.

  

Stage 10 — Partner Module

Goal

Support infertility care with partner profile.

Scope

Partner data, current/historical partner, semen analysis notes, journey link.

Deliverables

Partner model

Current partner

Partner history

Infertility Journey link

Partner documents

Partner summary

Suggested Sprints

Sprint 10.1 — Partner Profile

Goal:

Add current partner to patient.

Sprint 10.2 — Partner Infertility Data

Goal:

Add semen analysis summary and investigation notes.

Sprint 10.3 — Historical Partner Handling

Goal:

Preserve old partner history.

Acceptance Criteria

Patient may have multiple historical partners.

Only one current partner.

Partner may link to Infertility Journey.

Changing partner does not rewrite old infertility history.

  

Stage 11 — Finance Module

Goal

Track clinic income, discounts, free services, expenses, salaries, surgery finance.

Scope

Payments, expenses, salaries, service prices, reports.

Deliverables

Payment model

Expense model

Salary model

Service prices

Finance categories

Patient financial summary

Discount/free service tracking

Daily/monthly reports

Suggested Sprints

Sprint 11.1 — Service Prices

Goal:

Configure consultation, follow-up, CTG, procedures.

Sprint 11.2 — Patient Payments

Goal:

Record patient-linked payments.

Sprint 11.3 — Discounts & Free Services

Goal:

Track waived/discounted income.

Sprint 11.4 — Expenses & Salaries

Goal:

Record clinic spending.

Sprint 11.5 — Surgery Finance

Goal:

Track operation financial breakdown.

Sprint 11.6 — Finance Reports

Goal:

Daily/monthly income, expenses, net, patient account.

Acceptance Criteria

Most income links to Patient.

General income allowed.

Free/discounted service is recorded intentionally.

Payment edits require reason/audit.

Doctor has full finance access.

Reception has limited operational access.

  

Stage 12 — Notifications

Goal

Create simple actionable notification system.

Scope

Pending labs, missed follow-up, incomplete visit, upcoming surgery, finance alerts.

Deliverables

Notification model

Notification panel

Read/snooze/resolve

Patient-specific alerts

Home Dashboard alerts

Suggested Sprints

Sprint 12.1 — Notification Foundation

Goal:

Create notification infrastructure.

Sprint 12.2 — Clinical Notifications

Pending labs

Abnormal results

Incomplete visits

Missed follow-up

Sprint 12.3 — Surgery & Finance Notifications

Upcoming surgery

Pending histopathology

Outstanding payment

Acceptance Criteria

Notifications are actionable.

No notification noise.

Role-based visibility.

Each notification links to patient/object.

  

Stage 13 — Reports

Goal

Turn clinic data into useful summaries.

Scope

Clinical, operational, surgery, investigation, finance reports.

Deliverables

Reports workspace

Date filters

Clinical reports

Finance reports

Surgery reports

Export/print foundation

Suggested Sprints

Sprint 13.1 — Operational Reports

Daily clinic

Monthly visits

Appointments

No-shows

Sprint 13.2 — Clinical Reports

Active pregnancies

Infertility cases

High-risk patients

Follow-up compliance

Sprint 13.3 — Finance Reports

Daily income

Monthly income

Expenses

Net

Discount/free summary

Sprint 13.4 — Surgery & Investigation Reports

Upcoming surgeries

Completed surgeries

Pending histopathology

Pending labs

Abnormal results

Acceptance Criteria

Reports are useful, not decorative.

Reports are filterable.

Reports can be printed/exported.

Role-based data visibility.

  

Stage 14 — Settings & Administration

Goal

Allow clinic configuration without code changes.

Scope

Clinic settings, calendar, print templates, finance prices, users, backup settings.

Deliverables

Clinic profile

User management

Role management

Calendar settings

Finance settings

Print settings

Backup settings

AI settings placeholder

Suggested Sprints

Sprint 14.1 — Clinic Settings

Clinic name

Logo

Address

Phones

Working hours

Sprint 14.2 — User Management

Create users

Assign roles

Activate/deactivate

Sprint 14.3 — Calendar & Finance Settings

Appointment duration

Clinic days

Service prices

Finance categories

Sprint 14.4 — Print & Backup Settings

Prescription header

Report footer

Manual backup

Scheduled backup config

Acceptance Criteria

Admin can configure clinic.

Doctor/Owner controls critical settings.

Reception has limited settings.

Sensitive settings changes audited.

  

Stage 15 — Backup, Deployment, and Production Readiness

Goal

Prepare the app for real clinic use.

Scope

Backups, deployment, security, performance, documentation.

Deliverables

Manual backup

Scheduled backup

PostgreSQL backup

Uploads backup

Production config

Gunicorn/Nginx plan

HTTPS

Environment secrets

Deployment guide

Suggested Sprints

Sprint 15.1 — Backup System

Manual backup

Scheduled automatic backup

Restore instructions

Sprint 15.2 — Production Configuration

.env production

Logging

Error handling

Security headers

Database URL

Upload path

Sprint 15.3 — Cloud Deployment Trial

Deploy to private server/cloud.

Test from desktop/iPad/mobile.

Sprint 15.4 — Performance Pass

Patient search

Patient workspace

Today’s clinic

Timeline

Reports

Acceptance Criteria

Can backup database and uploads.

Can restore from backup.

Can access from iPad/mobile securely.

No debug config in production.

Core pages load fast.

  

Stage 16 — AI-Ready Foundation, Not Full AI

Goal

Prepare AI integration without letting AI modify records.

Scope

Structured context exports, AI draft placeholders, manual review.

Deliverables

Patient context builder

Visit context builder

Timeline context builder

AI draft interface placeholder

AI approval rule

Suggested Sprints

Sprint 16.1 — Context Builder

Build structured patient summary from DB.

Sprint 16.2 — AI Draft Placeholder

Store AI draft text only after doctor review later.

Sprint 16.3 — Missing Data Rules

Simple non-AI missing data checks.

Acceptance Criteria

AI cannot write automatically.

Doctor approves everything.

Database is structured enough for future AI.

  

Stage 17 — Testing, Freeze Review, and Launch

Goal

Make the system safe enough for real use.

Scope

Testing, bug fixing, freeze review, launch checklist.

Deliverables

Automated tests

Manual testing checklist

Permission tests

Migration tests

Backup test

Launch checklist

Known issues list

Testing Areas

Auth

RBAC

Patient CRUD

Search

Visit workflow

Appointment workflow

Prescription printing

Investigation pending/reviewed

Document upload

Surgery calendar

Finance entries

Audit logs

Backup/restore

Freeze Review Checklist

Models

Migrations

Routes

Services

Forms

Templates

Permissions

Audit

Tests

Documentation

Backup

No migration drift

No unrelated changes

  

Recommended MVP Boundary

MVP Must Include

Auth/RBAC

Patients

Search

Patient Workspace

Journeys

Visits

Appointments

Today’s Clinic

Prescription + Printing

Investigations + Presets

Documents

Basic Ultrasound

Basic Surgery

Basic Finance

Notifications

Settings

Backup

MVP Can Delay

Advanced AI

Drug interaction engine

PACS/DICOM

WhatsApp integration

Patient portal

Mobile app

Advanced analytics

Video storage

Full multi-clinic

CI/CD automation

  

Practical Build Order

أفضل ترتيب تنفيذ حقيقي:

0. Project Foundation

1. Auth + RBAC + Audit

2. Patients + Search + Workspace

3. Journey + Visit

4. Appointment + Today’s Clinic

5. Prescription + Print Engine

6. Investigations + Presets

7. Documents + Storage

8. Ultrasound

9. Surgery

10. Partner

11. Finance

12. Notifications

13. Reports

14. Settings

15. Backup + Deployment

16. AI-ready Context

17. Testing + Launch

ده ترتيب عملي لأن كل مرحلة تبني فوق اللي قبلها، ومفيش Module هيتنفذ قبل الأساس اللي محتاجه.

  

Project Governance

لكل Sprint لازم يكون فيه

Goal

Scope

Files to create

Files to modify

Database impact

Routes

Services

Forms

Templates

Permissions

Tests

Documentation

Acceptance criteria

Manual testing checklist

PowerShell verification commands

ممنوع اعتبار Sprint مكتمل إلا بعد

Developer applied code

Developer ran migrations

Developer ran tests

Developer provided output

Review done

Corrections applied

Git status reviewed

Commit message suggested

  

Suggested First Real Sprint

Sprint 0.1 — Flask Project Foundation

Goal:

Create clean Flask foundation for Nada Clinic System.

  

Scope:

App factory

Config

Extensions

Base layout

Static assets

Health route

Test setup

  

Database impact:

None or initial Alembic only

  

Routes:

GET /health

GET /

  

Templates:

base.html

home_placeholder.html

  

Tests:

App starts

Health route returns OK

  

Manual verification:

flask run

pytest

NEXT ACTION

ابدأ بـ Sprint 0.1 — Flask Project Foundation فقط، وبعد الموافقة نطلع له خطة Sprint تفصيلية بالملفات والأوامر قبل أي كود.