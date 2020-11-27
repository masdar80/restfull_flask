import datetime
from os.path import dirname, join

from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response

UPLOAD_FOLDER = 'F:\\uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI="sqlite:///" + join(dirname(dirname(__file__)), "database.sqlite"),
)
db = SQLAlchemy(app)


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    father_name = db.Column(db.String(100))
    birthday = db.Column(db.Date, default=datetime.date.today())
    gender = db.Column(db.String(45))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, first_name, last_name, father_name, birthday, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.father_name = father_name
        self.birthday = birthday
        self.gender = gender

    def __repr__(self):
        return '' % self.id


class PatientSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Patient
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    father_name = fields.String(required=False)
    birthday = fields.Date(required=True)
    gender = fields.String(required=True)


class Visits(db.Model):
    __tablename__ = "patient_visits"
    idpatient_visits = db.Column(db.Integer, primary_key=True)
    patient_visit_patient_id = db.Column(db.Integer)
    patient_visit_state = db.Column(db.String(100))
    patient_visit_desc = db.Column(db.Text)
    patient_visit_pain_degree = db.Column(db.Integer)
    patient_visit_company = db.Column(db.String(45))
    patient_visit_date = db.Column(db.Date)
    patient_visits_image = db.Column(db.Text)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, patient_visit_patient_id, patient_visit_state, patient_visit_desc, patient_visit_pain_degree,
                 patient_visit_company, patient_visit_date, patient_visits_image):
        self.patient_visit_patient_id = patient_visit_patient_id
        self.patient_visit_state = patient_visit_state
        self.patient_visit_desc = patient_visit_desc
        self.patient_visit_pain_degree = patient_visit_pain_degree
        self.patient_visit_company = patient_visit_company
        self.patient_visit_date = patient_visit_date
        self.patient_visits_image = patient_visits_image

    def __repr__(self):
        return '' % self.idpatient_visits


class VisitsSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Visits
        sqla_session = db.session

    idpatient_visits = fields.Number(dump_only=True)
    patient_visit_patient_id = fields.Number(required=True)
    patient_visit_state = fields.String(required=False)
    patient_visit_desc = fields.String(required=False)
    patient_visit_pain_degree = fields.Number(required=False)
    patient_visit_company = fields.String(required=False)
    patient_visit_date = fields.Date(required=False)
    patient_visits_image = fields.String(required=False)


db.create_all()
