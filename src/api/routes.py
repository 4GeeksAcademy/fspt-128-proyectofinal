from flask import request, jsonify, Blueprint
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy import select


from api.models import db, Profesor, TutorLegal, Estudiantes, Aula, Eventos, SuperAdmin, Asignaturas

api = Blueprint('api', __name__)
CORS(api)

def admin_required():
    user_id = get_jwt_identity()
    user = SuperAdmin.query.get(user_id)
    if not user or user.rol_id != 1:
        return jsonify({"msg": "Solo admin"}), 403
    return None
def profe_required():
    user_id = get_jwt_identity()
    user = Profesor.query.get(user_id)
    if not user or user.rol_id != 2:
        return jsonify({"msg": "Solo profesor"}), 403
    return None
def tutorLegal_required():
    user_id = get_jwt_identity()
    user = TutorLegal.query.get(user_id)
    if not user or user.rol_id != 3:
        return jsonify({"msg": "Solo tutor legal"}), 403
    return None

#SUPERADMIN REGISTRO, LOGIN Y GET#
@api.route('/superadmin/registro', methods=['POST'])
def registro_superadmin():
    data = request.get_json()
    email = data.get('email')
    rol_id = data.get('rol_id')
    password = data.get('password')
    nombre_colegio = data.get('nombre_colegio')

    if not email or not password or not rol_id or not nombre_colegio:
        return jsonify({'msg': 'Por favor completar todos los campos'}), 400

    existing_user = db.session.execute(
        select(SuperAdmin).where(SuperAdmin.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({'msg': 'Ya existe un administrador con este correo'}), 409

    new_user = SuperAdmin(
        email=email,
        rol_id=rol_id,
        password=password,
        nombre_colegio=nombre_colegio
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'Administrador creado correctamente'}), 200

@api.route('/superadmin/login', methods=['POST'])
def login_superadmin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'msg': 'Correo y contraseña requeridos'}), 400

    existing_user = db.session.execute(
        select(SuperAdmin).where(SuperAdmin.email == email)
    ).scalar_one_or_none()

    if existing_user is None:
        return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401

    if existing_user.check_password(password):
        access_token = create_access_token(
            identity=str(existing_user.id),
            additional_claims={
                "rol_id": existing_user.rol_id,
                "email": existing_user.email,
                "nombre_colegio": existing_user.nombre_colegio
            }
        )

        return jsonify({
            'msg': 'Inicio de sesión exitoso',
            'token': access_token,
            'existing_user': existing_user.serialize()
        }), 200

    return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401

@api.route('perfil/superadmin', methods=['GET'])
@jwt_required()
def perfil_superadmin():
    user = get_jwt_identity()
    existing_user = db.session.get(SuperAdmin, int(user["id"]))

    if not existing_user:
        return jsonify({"msg": "Usuario no encontrado"}), 400

    return jsonify(existing_user.serialize()), 200

#CERRAR SESION#
@api.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout correcto"}), 200

#EVENTOS#
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
    if user["rol_id"] not in [1, 2]:
        return jsonify({"msg": "Solo profesores"}), 403

    evento = Eventos.query.get(id)
    if not evento:
        return jsonify({"msg": "Evento no encontrado"}), 404

    db.session.delete(evento)
    db.session.commit()
    return jsonify({"msg": "Evento eliminado"}), 200

#mensajeria#
# @api.route('/messages', methods=['POST'])
# @jwt_required()
# def send_message():
#     user = get_jwt_identity()
#     if user["rol_id"] not in [2, 3]:
#         return jsonify({"msg": "Solo profesor o tutor"}), 403
#     return jsonify({"msg": "Mensaje enviado"}), 201

# @api.route('/messages', methods=['GET'])
# @jwt_required()
# def get_messages():
#     user = get_jwt_identity()
#     if user["rol_id"] not in [2, 3]:
#         return jsonify({"msg": "No autorizado"}), 403
#     return jsonify({"msg": "Lista de mensajes"}), 200

# def admin_required():
#     if get_jwt_identity()["rol_id"] != 1:
#         return jsonify({"msg": "Solo admin"}), 403

#PROFESORES#
@api.route('/teachers', methods=['POST'])
@jwt_required()
def create_teacher():
    admin_check = admin_required()
    if admin_check: return admin_check

    data = request.json
    teacher = Profesor(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        telephone=data.get("telephone"),
        rol_id=data.get("rol_id")
    )

    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.serialize()), 201

@api.route('/profesor/login',methods=['POST'])
def login_profesor():
    
    data= request.get_json()
    email= data.get('email')
    password= data.get('password')

    if not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400

    existing_user= db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

    if existing_user is None:
        return jsonify ({'msg':'El correo eletrócnico o contraseña son incorrectos'}),401

    if existing_user.check_password(password):
        access_token = create_access_token(
            identity=str(existing_user.id),
            additional_claims={
                "rol_id": existing_user.rol_id,
                "email": existing_user.email,
                "aula_id": Aula.aula_id,
                "curso": Aula.curso,
                "clase": Aula.clase
            }
        )

        return jsonify({
            'msg': 'Inicio de sesión exitoso',
            'token': access_token,
            'existing_user': existing_user.serialize()
        }), 200

    return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401                                                                                                                                                                                               


@api.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    admin_check = admin_required()
    if admin_check: return admin_check

    teachers = Profesor.query.all()
    return jsonify([t.serialize() for t in teachers]), 200

@api.route('/teachers/<int:id>', methods=['PUT'])
@jwt_required()
def update_teacher(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    teacher = Profesor.query.get(id)
    if not teacher:
        return jsonify({"msg": "Profesor no encontrado"}), 404

    data = request.json
    for key, value in data.items():
        setattr(teacher, key, value)

    db.session.commit()
    return jsonify(teacher.serialize()), 200

@api.route('/teachers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    teacher = Profesor.query.get(id)
    if not teacher:
        return jsonify({"msg": "Profesor no encontrado"}), 404

    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"msg": "Profesor eliminado"}), 200

#ESTUDIANTES#
@api.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    admin_check = admin_required()
    if admin_check: 
        return admin_check

    data = request.json
    student = Estudiantes(
        name=data.get("name"),
        profesor_id=data.get("profesor_id"),
        aula_id=data.get("aula_id")
    )

    db.session.add(student)
    db.session.commit()
    return jsonify(student.serialize()), 201

@api.route('/students/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    student = Estudiantes.query.get(id)
    if not student:
        return jsonify({"msg": "Estudiante no encontrado"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"msg": "Estudiante eliminado"}), 200

#TUTOR LEGAL#
@api.route('/tutors', methods=['POST'])
@jwt_required()
def create_tutor():
    admin_check = admin_required()
    if admin_check: return admin_check

    data = request.json
    tutor = TutorLegal(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        telephone=data.get("telephone"),
        rol_id=data.get("rol_id")
    )

    db.session.add(tutor)
    db.session.commit()
    return jsonify(tutor.serialize()), 201

@api.route('/tutors/<int:id>', methods=['PUT'])
@jwt_required()
def update_tutor(id):
    admin_check = admin_required()
    if admin_check: return admin_check

    tutor = TutorLegal.query.get(id)
    if not tutor:
        return jsonify({"msg": "Tutor no encontrado"}), 404

    data = request.json
    for key, value in data.items():
        setattr(tutor, key, value)

    db.session.commit()
    return jsonify(tutor.serialize()), 200

#AULAS#
@api.route('/crear/aula', methods=['POST'])
@jwt_required()
def crear_aula():
    admin_check = profe_required()
    if admin_check: return admin_check

    data = request.json    
    classroom = Aula(
        curso=data.get("curso"),
        clase=data.get("clase"),
        profesor_id=data.get("profesor_id"),
        colegio_id=data.get("colegio_id")
    )

    db.session.add(classroom)
    db.session.commit()
    return jsonify(classroom.serialize()), 201

@api.route('/eliminar/aula/<int:id>/<string:clase>', methods=['DELETE'])
@jwt_required()
def eliminar_aula(id, clase):
   
    admin_check = admin_required()
    if admin_check: 
        return admin_check

    aula = Aula.query.filter_by(aula_id=id, clase=clase).first()
    
    if not aula:
        return jsonify({
            "msg": "No se encontró un aula con ese ID y nombre de clase coincidentes."
        }), 404

  
    if aula.profesor_id is not None or len(aula.estudiantes) > 0:
        return jsonify({
            "msg": "No se puede eliminar: El aula debe estar totalmente vacía, asigne a los profesor/alumnos antes a otras aulas.",
            "detalles": {
                "profesor_asignado": aula.profesor_id is not None,
                "alumnos_inscritos": len(aula.estudiantes)
            }
        }), 400

    
    try:
        db.session.delete(aula)
        db.session.commit()
        return jsonify({"msg": f"Aula '{clase}' (ID: {id}) eliminada con éxito"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error inesperado al eliminar",
            "error": str(e)
        }), 500

@api.route('/aulas', methods=['GET'])
def obtener_aulas():
 
    aulas = Aula.query.all()
    return jsonify([aula.serialize() for aula in aulas]), 200

@api.route('/aula/<int:id>', methods=['PUT'])
@jwt_required()

def actualizar_aula(id):

    admin_check = admin_required()
    if admin_check: 
        return admin_check
    
    aula = Aula.query.get(id)
    if not aula:
        return jsonify({"msg": "Aula no encontrada"}), 404
        
    body = request.get_json()
    aula.curso = body.get("curso", aula.curso)
    aula.clase = body.get("clase", aula.clase)
    aula.profesor_id = body.get("profesor_id", aula.profesor_id)

    if "estudiantes" in body:
        estudiantes_ids = body.get("estudiantes", [])
        nuevos_alumnos = Estudiantes.query.filter(Estudiantes.id.in_(estudiantes_ids)).all()
        aula.estudiantes = nuevos_alumnos

    db.session.commit()
    return jsonify({"msg": "Aula actualizada", "aula": aula.serialize()}), 200


# asignaturas

@api.route('/asignaturas', methods=['POST'])
@jwt_required()
def create_asignatura():
    admin_check = admin_required()
    if admin_check: 
        return admin_check

    data = request.get_json()
    nueva = Asignaturas(nombre_asignatura=data.get('nombre_asignatura'))
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"msg": "Asignatura troncal creada"}), 201


@api.route('/asignaturas/<int:id>', methods=['PUT'])
@jwt_required()
def update_asignatura(id):
    admin_check = admin_required()
    if admin_check: 
        return admin_check

   
    asignatura = db.session.get(Asignaturas, id)
    
    if not asignatura:
        return jsonify({"msg": "La asignatura no existe"}), 404

    
    data = request.get_json()
    nuevo_nombre = data.get('nombre_asignatura')

    if not nuevo_nombre:
        return jsonify({"msg": "El nuevo nombre de la asignatura es requerido"}), 400

    
    asignatura.nombre_asignatura = nuevo_nombre
    db.session.commit()

    return jsonify({
        "msg": "Asignatura actualizada correctamente",
        "asignatura": asignatura.serialize()
    }), 200



@api.route('/asignaturas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asignatura(id):
    admin_check = admin_required()
    if admin_check: 
        return admin_check
    
    asignatura = db.session.get(Asignaturas, id)
    if not asignatura:
        return jsonify({"msg": "No existe"}), 404
    
    db.session.delete(asignatura)
    db.session.commit()
    return jsonify({"msg": "Asignatura eliminada globalmente"}), 200

@api.route('/asignaturas', methods=['GET'])
@jwt_required()
def get_asignaturas():
    
    result = db.session.execute(select(Asignaturas)).scalars().all()
    asignaturas_list = [asignatura.serialize() for asignatura in result]

    return jsonify(asignaturas_list), 200