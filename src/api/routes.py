"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, User

api = Blueprint('api', __name__)

# Allow CORS requests to this API

CORS(api)

@api.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Faltan credenciales"}), 400

    return jsonify({"msg": "Login correcto", "token": "JWT_TOKEN"}), 200


@api.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Datos incompletos"}), 400

    return jsonify({"msg": "Usuario registrado"}), 201


@api.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout correcto"}), 200


@api.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    data = request.json

    if not data.get("title"):
        return jsonify({"msg": "Falta título"}), 400

    return jsonify({"msg": "Evento creado"}), 201


@api.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    user = get_jwt_identity()

    if user["role"] not in ["profesor", "padre"]:
        return jsonify({"msg": "No autorizado"}), 403

    return jsonify({"events": []}), 200


@api.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    return jsonify({"msg": f"Evento {event_id} actualizado"}), 200


@api.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    return jsonify({"msg": f"Evento {event_id} eliminado"}), 200


@api.route('/grades', methods=['POST'])
@jwt_required()
def create_grade():
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    data = request.json

    if not data.get("student_id") or not data.get("grade"):
        return jsonify({"msg": "Datos incompletos"}), 400

    return jsonify({"msg": "Nota creada"}), 201

@api.route('/grades/<int:student_id>', methods=['GET'])
@jwt_required()
def get_grades(student_id):
    user = get_jwt_identity()

    if user["role"] != "padre":
        return jsonify({"msg": "Solo padres"}), 403

    return jsonify({"grades": []}), 200

@api.route('/grades/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_grade(grade_id):
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    return jsonify({"msg": f"Nota {grade_id} actualizada"}), 200

@api.route('/grades/<int:grade_id>', methods=['DELETE'])
@jwt_required()
def delete_grade(grade_id):
    user = get_jwt_identity()

    if user["role"] != "profesor":
        return jsonify({"msg": "Solo profesores"}), 403

    return jsonify({"msg": f"Nota {grade_id} eliminada"}), 200

@api.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    user = get_jwt_identity()

    if user["role"] not in ["profesor", "padre"]:
        return jsonify({"msg": "No autorizado"}), 403

    data = request.json

    if not data.get("receiver_id") or not data.get("content"):
        return jsonify({"msg": "Datos incompletos"}), 400

    return jsonify({"msg": "Mensaje enviado"}), 201


@api.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user = get_jwt_identity()

    if user["role"] not in ["profesor", "padre"]:
        return jsonify({"msg": "No autorizado"}), 403

    return jsonify({"messages": []}), 200

@api.route('/teachers', methods=['POST'])
@jwt_required()
def create_teacher():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"msg": "Profesor creado"}), 201


@api.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"teachers": []}), 200

@api.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"msg": "Estudiante creado"}), 201

@api.route('/tutors', methods=['POST'])
@jwt_required()
def create_tutor():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"msg": "Tutor creado"}), 201

@api.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"msg": "Aula creada"}), 201

@api.route('/teacher-list', methods=['GET'])
@jwt_required()
def teacher_list():
    user = get_jwt_identity()

    if user["role"] != "admin":
        return jsonify({"msg": "Solo admin"}), 403

    return jsonify({"teacher_list": []}), 200