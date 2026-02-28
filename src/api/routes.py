"""
API Routes - Portal Educativo
"""
from flask import request, jsonify, Blueprint
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.models import db, Profesor, TutorLegal, Estudiantes, Aula, Eventos, Calificaciones

api = Blueprint('api', __name__)
CORS(api)

@api.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    user = get_jwt_identity()

    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    data = request.json

    evento = Eventos(
        nombre_evento=data.get("nombre_evento"),
        localizacion=data.get("localizacion"),
        tipo_de_evento=data.get("tipo_de_evento"),
        profesor_id=user["id"]
    )

    db.session.add(evento)
    db.session.commit()

    return jsonify(evento.serialize()), 201

@api.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    user = get_jwt_identity()

    if user["rol_id"] not in [1, 2, 3]:
        return jsonify({"msg": "No autorizado"}), 403

    eventos = Eventos.query.all()

    return jsonify([e.serialize() for e in eventos]), 200

@api.route('/grades', methods=['POST'])
@jwt_required()
def create_grade():
    user = get_jwt_identity()

    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    data = request.json

    grade = Calificaciones(
        calificacion=data.get("calificacion"),
        asignatura_id=data.get("asignatura_id"),
        estudiante_id=data.get("estudiante_id")
    )

    db.session.add(grade)
    db.session.commit()

    return jsonify(grade.serialize()), 201

@api.route('/grades/<int:student_id>', methods=['GET'])
@jwt_required()
def get_grades(student_id):
    user = get_jwt_identity()

    if user["rol_id"] not in [2, 3]:
        return jsonify({"msg": "No autorizado"}), 403

    grades = Calificaciones.query.filter_by(estudiante_id=student_id).all()

    return jsonify([g.serialize() for g in grades]), 200

@api.route('/teachers', methods=['POST'])
@jwt_required()
def create_teacher():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    data = request.json

    teacher = Profesor(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        telephone=data.get("telephone")
    )

    db.session.add(teacher)
    db.session.commit()

    return jsonify(teacher.serialize()), 201

@api.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    teachers = Profesor.query.all()

    return jsonify([t.serialize() for t in teachers]), 200

@api.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    data = request.json

    student = Estudiantes(
        name=data.get("name"),
        profesor_id=data.get("profesor_id"),
        aula_id=data.get("aula_id")
    )

    db.session.add(student)
    db.session.commit()

    return jsonify(student.serialize()), 201


@api.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    students = Estudiantes.query.all()

    return jsonify([s.serialize() for s in students]), 200

@api.route('/students/<int:id>', methods=['PUT'])
@jwt_required()
def update_student(id):
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    student = Estudiantes.query.get(id)

    if not student:
        return jsonify({"msg": "Estudiante no encontrado"}), 404

    data = request.json

    student.name = data.get("name", student.name)
    student.profesor_id = data.get("profesor_id", student.profesor_id)
    student.aula_id = data.get("aula_id", student.aula_id)

    db.session.commit()

    return jsonify(student.serialize()), 200

@api.route('/tutors', methods=['POST'])
@jwt_required()
def create_tutor():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    data = request.json

    tutor = TutorLegal(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        telephone=data.get("telephone")
    )

    db.session.add(tutor)
    db.session.commit()

    return jsonify(tutor.serialize()), 201

@api.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():
    user = get_jwt_identity()

    if user["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

    data = request.json

    classroom = Aula(
        curso=data.get("curso"),
        clase=data.get("clase"),
        profesor_id=data.get("profesor_id")
    )

    db.session.add(classroom)
    db.session.commit()

    return jsonify(classroom.serialize()), 201