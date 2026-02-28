from flask import request, jsonify, Blueprint
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.models import db, Profesor, TutorLegal, Estudiantes, Aula, Eventos, Calificaciones

api = Blueprint('api', __name__)
CORS(api)

@api.route('/login', methods=['POST'])
def login():
    return jsonify({"msg": "Login completado"}), 200

@api.route('/register', methods=['POST'])
def register():
    return jsonify({"msg": "Registro solo SuperAdmin"}), 200

@api.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout correcto"}), 200

@api.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    data = request.json
    if not data.get("nombre_evento"):
        return jsonify({"msg": "Falta nombre_evento"}), 400

    evento = Eventos(
        nombre_evento=data["nombre_evento"],
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
    eventos = Eventos.query.all()
    return jsonify([e.serialize() for e in eventos]), 200

@api.route('/events/<int:id>', methods=['PUT'])
@jwt_required()
def update_event(id):
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    evento = Eventos.query.get(id)
    if not evento:
        return jsonify({"msg": "Evento no encontrado"}), 404

    data = request.json
    evento.nombre_evento = data.get("nombre_evento", evento.nombre_evento)
    evento.localizacion = data.get("localizacion", evento.localizacion)

    db.session.commit()
    return jsonify(evento.serialize()), 200

@api.route('/events/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    evento = Eventos.query.get(id)
    if not evento:
        return jsonify({"msg": "Evento no encontrado"}), 404

    db.session.delete(evento)
    db.session.commit()
    return jsonify({"msg": "Evento eliminado"}), 200

@api.route('/grades', methods=['POST'])
@jwt_required()
def create_grade():
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    grade = Calificaciones(**request.json)
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

@api.route('/grades/<int:id>', methods=['PUT'])
@jwt_required()
def update_grade(id):
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    grade = Calificaciones.query.get(id)
    if not grade:
        return jsonify({"msg": "Nota no encontrada"}), 404

    grade.calificacion = request.json.get("calificacion", grade.calificacion)
    db.session.commit()
    return jsonify(grade.serialize()), 200

@api.route('/grades/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_grade(id):
    user = get_jwt_identity()
    if user["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403

    grade = Calificaciones.query.get(id)
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"msg": "Nota eliminada"}), 200

@api.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    user = get_jwt_identity()
    if user["rol_id"] not in [2, 3]:
        return jsonify({"msg": "Solo profesor o tutor"}), 403

    return jsonify({"msg": "Mensaje enviado"}), 201

@api.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user = get_jwt_identity()
    if user["rol_id"] not in [2, 3]:
        return jsonify({"msg": "No autorizado"}), 403

    return jsonify({"msg": "Lista de mensajes"}), 200

def admin_required():
    if get_jwt_identity()["rol_id"] != 1:
        return jsonify({"msg": "Solo admin"}), 403

@api.route('/teachers', methods=['POST'])
@jwt_required()
def create_teacher():
    admin_check = admin_required()
    if admin_check: return admin_check

    teacher = Profesor(**request.json)
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.serialize()), 201

@api.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    admin_check = admin_required()
    if admin_check: return admin_check

    teachers = Profesor.query.all()
    return jsonify([t.serialize() for t in teachers]), 200

@api.route('/teachers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    teacher = Profesor.query.get(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"msg": "Profesor eliminado"}), 200

@api.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    admin_check = admin_required()
    if admin_check: return admin_check

    student = Estudiantes(**request.json)
    db.session.add(student)
    db.session.commit()
    return jsonify(student.serialize()), 201

@api.route('/students/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    student = Estudiantes.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"msg": "Estudiante eliminado"}), 200

@api.route('/tutors', methods=['POST'])
@jwt_required()
def create_tutor():
    admin_check = admin_required()
    if admin_check: return admin_check

    tutor = TutorLegal(**request.json)
    db.session.add(tutor)
    db.session.commit()
    return jsonify(tutor.serialize()), 201

@api.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():
    admin_check = admin_required()
    if admin_check: return admin_check

    classroom = Aula(**request.json)
    db.session.add(classroom)
    db.session.commit()
    return jsonify(classroom.serialize()), 201