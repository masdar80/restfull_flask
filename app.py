import base64
import os
import os.path
from datetime import datetime, date
from os import path
import flask
from flask import make_response, send_file
from flask import Flask, request, redirect, jsonify
from sqlalchemy import engine
from werkzeug.utils import secure_filename
from resources.Patient import Patient, PatientSchema, db, app, ALLOWED_EXTENSIONS, Visits, VisitsSchema
from pain_recognition.prediction import get_prediction_result, getresult

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

session = Session(bind=engine)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/test', methods=['GET'])
def visits_group_by():
    get_visits = db.session.query(func.count(Visits.idpatient_visits).label('total')).group_by(
        Visits.patient_visit_company).all()
    print(get_visits)


# TESTTTTTTTTTTTTTTTTTT image
@app.route('/get_image')
def get_image():
    filename = 'F:\\uploads\\3\\06-10-2020_15-19-49_Pain2.jpg'
    return send_file(filename, mimetype='image/gif')


@app.route('/get_image1')
def get_image1():
    img_path = 'F:\\uploads\\3\\06-10-2020_15-19-49_Pain2.jpg'
    img = get_encoded_img(img_path)
    # prepare the response: data
    value1 = 5
    value2 = 'skata'
    response_data = {"key1": value1, "key2": value2, "image": img}
    return make_response(jsonify(response_data))


@app.route('/get_visits_with_img/<_id>', methods=['GET'])
def get_visits_with_img(_id):
    get_visits = Visits.query.filter_by(patient_visit_patient_id=_id).all()
    visit_schema = VisitsSchema(many=True)
    visit = visit_schema.dump(get_visits)
    for i in range(len(visit)):
        img_path = visit[i]['patient_visits_image']
        if img_path == 'no image':
            visit[i]['patient_visits_image'] = 'no image'
        else:
            img = get_encoded_img(img_path)
            visit[i]['patient_visits_image'] = img
    return make_response(jsonify(visit))


@app.route('/get_visit_with_img/<_id>', methods=['GET'])
def get_visit_with_img(_id):
    get_visits = Visits.query.get(_id)
    visit_schema = VisitsSchema()
    visit = visit_schema.dump(get_visits)

    img_path = visit['patient_visits_image']
    if img_path == 'no image':
        visit['patient_visits_image'] = 'no image'
    else:
        img = get_encoded_img(img_path)
        visit['patient_visits_image'] = img
    return make_response(jsonify(visit))


# print(visit[1]['patient_visits_image'])

def get_encoded_img(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


###########################################################3

@app.route('/visits', methods=['GET'])
def get_visits_all():
    get_visits = Visits.query.all()
    visit_schema = VisitsSchema(many=True)
    visits = visit_schema.dump(get_visits)
    return make_response(jsonify(visits))


@app.route('/visits/<_id>', methods=['GET'])
def get_visit_by_id(_id):
    get_visit = Visits.query.get(_id)
    visit_schema = VisitsSchema()
    visit = visit_schema.dump(get_visit)
    return make_response(jsonify(visit))


@app.route('/patient_visits/<_id>', methods=['GET'])
def get_visit_by_patient_id(_id):
    get_visits = Visits.query.filter_by(patient_visit_patient_id=_id).all()
    visit_schema = VisitsSchema(many=True)
    visit = visit_schema.dump(get_visits)
    return make_response(jsonify(visit))


@app.route('/visits/<_id>', methods=['PUT'])
def update_visit_by_id(_id):
    get_visit = Visits.query.get(_id)
    if not get_visit:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 800
        return resp
    if request.form.get('patient_visit_patient_id'):
        get_visit.patient_visit_patient_id = request.form['patient_visit_patient_id']
    else:
        resp = jsonify({'message': 'يجب تحديد المريض'})
        resp.status_code = 400
        return resp
    if request.form.get('patient_visit_state'):
        get_visit.patient_visit_state = request.form['patient_visit_state']
    if request.form.get('patient_visit_desc'):
        get_visit.patient_visit_desc = request.form['patient_visit_desc']
    if request.form.get('patient_visit_company'):
        get_visit.patient_visit_company = request.form['patient_visit_company']
    if request.form.get('patient_visit_pain_degree'):
        get_visit.patient_visit_pain_degree = request.form['patient_visit_pain_degree']
    else:
        get_visit.patient_visit_pain_degree = -1
    if request.form.get('patient_visit_date'):
        str_birthday = request.form['patient_visit_date']
        if str_birthday == '':
            today = date.today()
            str_birthday = today.strftime("%Y-%m-%d")
        get_visit.patient_visit_date = datetime.strptime(str_birthday, '%Y-%m-%d')
    if 'patient_visits_image' in request.files:
        file = request.files['patient_visits_image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], get_visit.patient_visit_patient_id)
            print(upload_directory)
            # datetime object containing current date and time
            now = datetime.now()
            print("now =", now)
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
            filepath = os.path.join(upload_directory, dt_string + '_' + filename)
            print("old path:" + filepath)

            if not path.exists(upload_directory):
                os.mkdir(upload_directory)
            file.save(filepath)

            get_visit.patient_visits_image = filepath
            # Get Pain Degree From Image
            # get_prediction_result(filepath)

            filepath = filepath.replace("\\", "/")
            print("new path:" + filepath)
            print(get_prediction_result(filepath))
        # get_visit.patient_visit_pain_degree = request.form['patient_visit_pain_degree']
        else:
            resp = jsonify({'message': 'مشكلة باسم الصورة'})
            resp.status_code = 400
            return resp
    db.session.add(get_visit)
    db.session.commit()
    visit_schema = VisitsSchema()
    visit = visit_schema.dump(get_visit)
    return make_response(jsonify(visit))


@app.route('/visits/<_id>', methods=['DELETE'])
def delete_visit_by_id(_id):
    get_visit = Visits.query.get(_id)
    if not get_visit:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 800
        return resp
    db.session.delete(get_visit)
    db.session.commit()
    return make_response("", 204)


@app.route('/visits', methods=['POST'])
def create_visit():
    # patient_visit_pain_degree = 5
    patient_visits_image = ''
    if request.form.get('patient_visit_patient_id'):
        patient_visit_patient_id = request.form['patient_visit_patient_id']
    else:
        resp = jsonify({'message': 'يجب تحديد المريض'})
        resp.status_code = 400
        return resp
    if request.form.get('patient_visit_state'):
        patient_visit_state = request.form['patient_visit_state']
    if request.form.get('patient_visit_desc'):
        patient_visit_desc = request.form['patient_visit_desc']
    if request.form.get('patient_visit_company'):
        patient_visit_company = request.form['patient_visit_company']
    if request.form.get('patient_visit_pain_degree'):
        patient_visit_pain_degree = request.form['patient_visit_pain_degree']
    else:
        patient_visit_pain_degree = -1
    if request.form.get('patient_visit_date'):
        str_birthday = request.form['patient_visit_date']
        if str_birthday == '' or str_birthday is None:
            print("hereeeee1")
            today = date.today()
            str_birthday = today.strftime("%Y-%m-%d")
        patient_visit_date = datetime.strptime(str_birthday, '%Y-%m-%d')
    else:
        print("hereeeee2")
        today = date.today()
        str_birthday = today.strftime("%Y-%m-%d")
        patient_visit_date = datetime.strptime(str_birthday, '%Y-%m-%d')

    # patient_visits_image = ''
    if 'patient_visits_image' in request.files:
        file = request.files['patient_visits_image']
        if file and file.filename != '' and file.name is not None and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], patient_visit_patient_id)
            print(upload_directory)
            # datetime object containing current date and time
            now = datetime.now()
            print("nowww =", now)
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
            filepath = os.path.join(upload_directory, dt_string + '_' + filename)
            print(filepath)
            filepath = filepath.replace("\\", "/")
            print("new path:" + filepath)
            if not path.exists(upload_directory):
                os.mkdir(upload_directory)
            file.save(filepath)
            patient_visits_image = filepath
        else:
            patient_visits_image = 'no image'
    else:
        patient_visits_image = 'no image'
        # resp = jsonify({'message': 'مشكلة باسم الصورة'})
        # resp.status_code = 400
        # return resp
    print("IMAGE:::::::::")
    print(patient_visits_image)
    print("Degree:::::::::")
    print(patient_visit_pain_degree)
    print("Date:::::::::")
    print(patient_visit_date)

    visit = Visits(
        patient_visit_patient_id=patient_visit_patient_id,
        patient_visit_state=patient_visit_state,
        patient_visit_desc=patient_visit_desc,
        patient_visit_company=patient_visit_company,
        patient_visit_pain_degree=patient_visit_pain_degree,
        patient_visit_date=patient_visit_date,
        patient_visits_image=patient_visits_image
    )
    # visit = Visits(
    #     patient_visit_patient_id=patient_visit_patient_id,
    #     patient_visit_state=patient_visit_state,
    #     patient_visit_desc=patient_visit_desc,
    #     patient_visit_company=patient_visit_company,
    #     patient_visit_date=patient_visit_date
    # )
    visit_schema = VisitsSchema()
    db.session.add(visit)
    db.session.commit()

    result = visit_schema.dump(visit)
    return make_response(jsonify(result), 200)


@app.route('/patients', methods=['GET'])
def get_patents_all():
    get_patients = Patient.query.all()
    patients_schema = PatientSchema(many=True)
    patients = patients_schema.dump(get_patients)
    return make_response(jsonify(patients))


@app.route('/patients/<_id>', methods=['GET'])
def get_patient_by_id(_id):
    get_patient = Patient.query.get(_id)
    if not get_patient:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 800
        return resp
    patients_schema = PatientSchema()
    patient = patients_schema.dump(get_patient)
    return make_response(jsonify(patient))


@app.route('/patients/<_id>', methods=['DELETE'])
def delete_patient_by_id(_id):
    get_patient = Patient.query.get(_id)
    if not get_patient:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 801
        return resp
    db.session.delete(get_patient)
    db.session.commit()
    return make_response("", 204)


@app.route('/patients/<_id>', methods=['PUT'])
def update_patient_by_id(_id):
    get_patient = Patient.query.get(_id)
    if not get_patient:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 800
        return resp

    if request.form.get('first_name'):
        get_patient.first_name = request.form['first_name']
    if request.form.get('last_name'):
        get_patient.last_name = request.form['last_name']
    if request.form.get('father_name'):
        get_patient.father_name = request.form['father_name']
    if request.form.get('gender'):
        get_patient.gender = request.form['gender']
    if request.form.get('birthday'):
        str_birthday = request.form['birthday']
        # print(str_birthday)
        get_patient.birthday = datetime.strptime(str_birthday, '%Y-%m-%d')

    db.session.add(get_patient)
    db.session.commit()
    patient_schema = PatientSchema()
    patient = patient_schema.dump(get_patient)
    return make_response(jsonify(patient))


@app.route('/patients', methods=['POST'])
def create_patient():
    print(request.form)
    if request.form.get('first_name'):
        first_name = request.form['first_name']
    if request.form.get('last_name'):
        last_name = request.form['last_name']
    if request.form.get('father_name'):
        father_name = request.form['father_name']
    if request.form.get('gender'):
        gender = request.form['gender']
    if request.form.get('birthday'):
        str_birthday = request.form['birthday']
        # print(str_birthday)
        birthday = datetime.strptime(str_birthday, '%Y-%m-%d')

    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        father_name=father_name,
        gender=gender,
        birthday=birthday
    )
    patient_schema = PatientSchema()
    db.session.add(patient)
    db.session.commit()

    result = patient_schema.dump(patient)
    return make_response(jsonify(result), 200)


@app.route('/pain_degree', methods=['POST'])
def pain_mesurment():
    if 'patient_visits_image' in request.files:
        file = request.files['patient_visits_image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], 'degree_only')
            print(upload_directory)
            # datetime object containing current date and time
            now = datetime.now()
            print("now =", now)
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
            filepath = os.path.join(upload_directory, dt_string + '_' + filename)
            print(filepath)
            filepath = filepath.replace("\\", "/")
            print("new path:" + filepath)
            if not path.exists(upload_directory):
                os.mkdir(upload_directory)
            file.save(filepath)
            # Get Pain Degree From Image

            result = get_prediction_result(filepath)
            print(get_prediction_result(filepath))
        else:
            resp = jsonify({'message': 'مشكلة باسم الصورة'})
            resp.status_code = 400
            return resp
    return make_response(jsonify({'degree': result}))


@app.route('/update_visit_image/<_id>', methods=['POST'])
def update_visit_image_by_id(_id):
    get_visit = Visits.query.get(_id)
    if not get_visit:
        resp = jsonify({'message': 'no one '})
        resp.status_code = 800
        return resp

    if 'patient_visits_image' in request.files:
        file = request.files['patient_visits_image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], str(get_visit.patient_visit_patient_id))
            print(upload_directory)
            # datetime object containing current date and time
            now = datetime.now()
            print("now =", now)
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
            filepath = os.path.join(upload_directory, dt_string + '_' + filename)
            print(filepath)
            if not path.exists(upload_directory):
                os.mkdir(upload_directory)
            file.save(filepath)
            get_visit.patient_visits_image = filepath
            # Get Pain Degree From Image
            # get_prediction_result(filepath)
            calculated_degree = get_prediction_result(filepath)
            print("Pain Degree: patient_visit_pain_degree " + calculated_degree)
            get_visit.patient_visit_pain_degree = calculated_degree
            #get_visit.patient_visit_pain_degree = 1
        else:
            resp = jsonify({'message': 'مشكلة باسم الصورة'})
            print("Namee Problem")
            resp.status_code = 407
            return resp
    db.session.add(get_visit)
    db.session.commit()
    visit_schema = VisitsSchema()
    visit = visit_schema.dump(get_visit)
   # return make_response(jsonify(visit))
    print("Pain Degree: " + calculated_degree)
    return make_response(jsonify({'degree': calculated_degree}))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
