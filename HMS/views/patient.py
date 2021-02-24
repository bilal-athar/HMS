from flask import *
from flask import Blueprint, jsonify
from datetime import datetime

from HMS.models.doctors import Doctors, Patient

patient = Blueprint('patient', __name__)


@patient.route('/patient/add', methods=['POST'])
def add_patient():
    global status
    data = request.get_json()
    doctor_id = Doctors.objects.only('id').filter(id=data['doctor_id'])
    if not doctor_id:
        return jsonify(message="invalid doctor", category="error"), 400
    first_name = data["first_name"]
    if not first_name:
        return jsonify(message="first name required", category="error"), 400

    last_name = data["last_name"]
    if not last_name:
        return jsonify(message="last name required", category="error"), 400

    date = datetime.now()

    age = data["age"]
    disease_name = data["disease_name"]
    medicine_name = data["medicine_name"]
    cnic = data["cnic"]
    if medicine_name:
        try:
            doctor = get_doctor(data["doctor_id"])
            print("in function", doctor)
        except:
            return jsonify(message="doctor not found")
        if doctor == "doctor":
            status = "2"
        else:
            return jsonify(message="only doctor can assign medicine", category="error"), 400
    else:
        status = "1"
    patient = Patient()
    patient.doctor_id = doctor_id
    patient.first_name = first_name
    patient.last_name = last_name
    patient.date = date
    patient.age = age
    patient.disease_name = disease_name
    patient.medicine_name = medicine_name
    patient.cnic = cnic
    patient.status = status
    patient.save()
    return jsonify(message="successfully added", category="success", patient_id=str(patient.id)), 201


def get_doctor(doctor_id):
    doctor = Doctors.objects.filter(id=str(doctor_id)).get()
    doctor = doctor.user_type
    return doctor


@patient.route('/patient/update', methods=['PATCH'])
def update_patient():
    data = request.get_json()
    patient_id = data["patient_id"]
    if not patient_id:
        return jsonify(message="patient required", category="error", ), 400
    patient = Patient.objects(id=patient_id).get()
    doctor_id = Doctors.objects.only('id').filter(id=data['doctor_id'])
    if not doctor_id:
        return jsonify(message="invalid doctor", category="error"), 400
    disease_name = data["disease_name"]
    medicine_name = data["medicine_name"]
    if medicine_name:
        try:
            doctor = get_doctor(data["doctor_id"])
        except:
            return jsonify(message="doctor not found")
        if doctor == "doctor":
            status = "2"
        else:
            return jsonify(message="only doctor can assign medicine", category="error"), 400
    else:
        status = "1"
    try:
        patient.update(
            medicine_name=medicine_name,
            disease_name=disease_name,
            status=status
        )
        return jsonify(message="updated", category="success"), 200
    except:
        return jsonify(message="try again", category="error"), 400


@patient.route('/patient/update_status', methods=['PATCH'])
def update_patient_status():
    data = request.get_json()
    patient_id = data["patient_id"]
    if not patient_id:
        return jsonify(message="patient required", category="error", ), 400
    try:
        patient = Patient.objects(id=patient_id).get()
        if patient.status == "2":
            patient.update(status="3")
        else:
            return jsonify(message="not allowed", category="error"), 400
        return jsonify(message="updated", category="success"), 200
    except:
        return jsonify(message="try again", category="error"), 400


@patient.route('/patient/<doctor_id>', methods=['GET'])
def get_patient(doctor_id):
    data = []
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    patient = get_doctor(doctor_id)

    try:
        if patient == "doctor":
            patient = Patient.objects().filter(status="1", date__gte=start)
        elif patient == "medical_rep":
            patient = Patient.objects().filter(status="2", date__gte=start)
        for items in patient:
            data.append({
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })
        return jsonify(data)
    except:
        return jsonify(message="record not found", category="error"), 400


@patient.route('/patient/day/', methods=['GET'])
def day_patients():
    patients = []
    doctors = []
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)

    details = request.args.get('details')
    if details:
        doctor = Doctors.objects()
        for items in doctor:
            doctors.append(str(items.id))

        patient = Patient.objects().filter(status="3", date__gte=start)

        for items in patient:
            patients.append({
                "doctor_id": str(items.doctor_id[0].id),
                "doctor_name": str(items.doctor_id[0].name),
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })

        export = []
        for id in doctors:

            result = []
            for pat in patients:
                if pat['doctor_id'] == id:
                    result.append({"first_name": pat['first_name'], "last_name": pat['last_name'], "cnic": pat['cnic'],
                                   "disease_name": pat['disease_name'], "medicine_name": pat['medicine_name'],
                                   "age": pat['age']})
            dictDoctor = {"doctor_id": id, "patients": result, "total_patients": len(result)}
            export.append(dictDoctor)
        return jsonify(records=export), 200

    doctor_id = request.args.get('doctor_id')
    if doctor_id:
        patient = Patient.objects().filter(doctor_id=doctor_id, status="3", date__gte=start)
        for items in patient:
            patients.append({
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })
        return jsonify(by_doctor=patients, total_patients=len(patients)), 200
    try:
        patient = Patient.objects().filter(status="3", date__gte=start)
        for items in patient:
            patients.append({
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })
        return jsonify(records=patients, total_patients=len(patients)), 200
    except:
        return jsonify(message="record not found", category="error"), 400


@patient.route('/patient/year/', methods=['GET'])
def year_patients():
    patients = []
    doctors = []
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return jsonify(message="Incorrect Format, Try with YYYY-MM-DDTHH:MM:SS", category="error"), 400

    details = request.args.get('details')
    if details:
        doctor = Doctors.objects()
        for items in doctor:
            doctors.append(str(items.id))

        patient = Patient.objects().filter(status="3", date__gte=start, date__lt=end)

        for items in patient:
            patients.append({
                "doctor_id": str(items.doctor_id[0].id),
                "doctor_name": str(items.doctor_id[0].name),
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })

        export = []
        for id in doctors:

            result = []
            for pat in patients:
                if pat['doctor_id'] == id:
                    result.append({"first_name": pat['first_name'], "last_name": pat['last_name'], "cnic": pat['cnic'],
                                   "disease_name": pat['disease_name'], "medicine_name": pat['medicine_name'],
                                   "age": pat['age']})
            dictDoctor = {"doctor_id": id, "patients": result, "total_patients": len(result)}
            export.append(dictDoctor)
        return jsonify(records=export), 200

    doctor_id = request.args.get('doctor_id')
    if doctor_id:
        patient = Patient.objects().filter(doctor_id=doctor_id, status="3", date__gte=start, date__lt=end)
        for items in patient:
            patients.append({
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })
        return jsonify(by_doctor=patients, total_patients=len(patients)), 200
    try:
        patient = Patient.objects().filter(status="3", date__gte=start, date__lt=end)
        for items in patient:
            patients.append({
                "first_name": items.first_name,
                "last_name": items.last_name,
                "age": items.age,
                "disease_name": items.disease_name,
                "medicine_name": items.medicine_name,
                "cnic": items.cnic
            })
        return jsonify(records=patients, total_patients=len(patients)), 200
    except:
        return jsonify(message="record not found", category="error"), 400
