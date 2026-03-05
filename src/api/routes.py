from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import select
from flask_cors import CORS
from api.utils import generate_sitemap, APIException
from api.models import db, Profesor, TutorLegal, Estudiantes, Aula, Eventos, SuperAdmin
from flask import Flask, request, jsonify, url_for, Blueprint

This module takes care of starting the API Server, Loading the DB and Adding the endpoints


api = Blueprint('api', __name__)
CORS(api)


def admin_required():
    user = get_jwt_identity()
    if not user or user.get("rol_id") != 1:
        return jsonify({"msg": "Solo admin"}), 403
    return None

# SUPERADMIN REGISTRO, LOGIN Y GET#


@api.route('/superadmin/registro', methods=['POST'])
def registro_superadmin():
    data = request.get_json()
    email = data.get('email')
    rol_id = data.get('rol_id')
    password = data.get('password')
    nombre_colegio = data.get('nombre_colegio')

    if not email or not password or not rol_id or not nombre_colegio:
        return jsonify({'msg': 'Por favor completar todos los campos'}), 400

    existing_user = db.session.execute(select(SuperAdmin).where(
        SuperAdmin.email == email)).scalar_one_or_none()

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

    existing_user= db.session.execute(select(SuperAdmin).where(SuperAdmin.email == email)).scalar_one_or_none()
    if existing_user is None:
        return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401

    if existing_user.check_password(password):
        identity_data = {
    "id": existing_user.id,
    "rol_id": existing_user.rol_id,
    "email": existing_user.email,
    "nombre_colegio": existing_user.nombre_colegio
}

    access_token = create_access_token(identity=identity_data)
    return jsonify ({
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

# CERRAR SESION#


@api.route('/logout', methods=['POST'])
@jwt_required()
def logout():

return jsonify({"msg": "Logout correcto"}), 200

# EVENTOS#


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

# mensajeria#
# @api.route('/messages', methods=['POST'])
# @jwt_required()
# def send_message():
#      user = get_jwt_identity()
#      if user["rol_id"] not in [2, 3]:
#          return jsonify({"msg": "Solo profesor o tutor"}), 403
#      return jsonify({"msg": "Mensaje enviado"}), 201

# @api.route('/messages', methods=['GET'])
# @jwt_required()
# def get_messages():
#      user = get_jwt_identity()
#      if user["rol_id"] not in [2, 3]:
#          return jsonify({"msg": "No autorizado"}), 403
#      return jsonify({"msg": "Lista de mensajes"}), 200

# def admin_required():
#      if get_jwt_identity()["rol_id"] != 1:
#          return jsonify({"msg": "Solo admin"}), 403

# PROFESORES#


@api.route('profesor/registro', methods=['POST'])
def registro_tutorlegal():


        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        rol_id = data.get('rol_id')
        telephone = data.get('telephone')
        password = data.get('password')

         if  not email or not password or not rol_id or not name or not telephone:
                 return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400

        existing_user = db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

         if existing_user:
                 return jsonify({'msg': 'Un perfil de administrador con este correo electrócnico ya existe'}), 409



        new_user = Profesor(email= email, rol_id= rol_id, password= password, name=name, telephone= telephone)
        new_user.set_password(password)


        db.session.add(new_user)
        db.session.commit()

         return jsonify({'msg': 'El perfil de administrador ha sido creado satisfactoriamente'}), 200


@api.route('profesor/login', methods=['POST'])
def login_profesor():


          data = request.get_json()
          email = data.get('email')
          password = data.get('password')

           if  not email or not password:
                 return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400

          existing_user = db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

           if existing_user is None:
                 return jsonify ({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401

           if existing_user.check_password(password):
                  access_token = create_access_token(identity=str(existing_user.id))
                  return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}), 200

           else:
                 return jsonify({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401


@api.route('perfil/profesor', methods=['GET'])
@jwt_required()
def perfil_profesor():


        existing_user_id = get_jwt_identity()
        existing_user = db.session.get(Profesor, int(existing_user_id))
         if not existing_user:
                 return jsonify({"msg": "Usuario no encontrado"}), 400
        return jsonify(existing_user.serialize()), 200


@api.route('/teachers/<int:id>', methods=['PUT'])
@jwt_required()
def update_teacher(id):


        admin_check = admin_required()
        if admin_check:
             return admin_check

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
        if admin_check:
             return admin_check

        teacher = Profesor.query.get(id)
         if not teacher:
                 return jsonify({"msg": "Profesor no encontrado"}), 404

        db.session.delete(teacher)
        db.session.commit()
         return jsonify({"msg": "Profesor eliminado"}), 200

# ESTUDIANTES#
# ruta para crear estudiante


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

# ruta para eliminar estudiante


@api.route('/students/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):


        admin_check = admin_required()
        if admin_check:
             return admin_check

        student = Estudiantes.query.get(id)
         if not student:
                 return jsonify({"msg": "Estudiante no encontrado"}), 404

        db.session.delete(student)
        db.session.commit()
         return jsonify({"msg": "Estudiante eliminado"}), 200


# TUTOR LEGAL
# ruta para crear
@api.route('/tutors/', methods=['POST'])
@jwt_required()
def create_tutor():


        admin_check = admin_required()
        if admin_check:
             return admin_check

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

# ruta para modificar


@api.route('/tutors/<int:id>', methods=['PUT'])
@jwt_required()
def update_tutor(id):


        admin_check = admin_required()
        if admin_check:
             return admin_check

        tutor = TutorLegal.query.get(id)
         if not tutor:
                 return jsonify({"msg": "Tutor no encontrado"}), 404

        data = request.json
         for key, value in data.items():
                setattr(tutor, key, value)

        db.session.commit()
         return jsonify(tutor.serialize()), 200

# AULAS#
# ruta para crear aula


@api.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():


        admin_check = admin_required()
        if admin_check:
             return admin_check

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


@api.route('tutorlegal/login', methods=['POST'])
def login_tutor_legal():


        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

         if  not email or not password:
                 return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400

        existing_user = db.session.execute(select(TutorLegal).where(TutorLegal.email == email)).scalar_one_or_none()

         if existing_user is None:
                 return jsonify ({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401

         if existing_user.check_password(password):
                  access_token = create_access_token(identity=str(existing_user.id))
                  return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}), 200

         else:
                 return jsonify({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401


@api.route('perfil/tutorlegal', methods=['GET'])
@jwt_required()
def perfil_tutorlegal():


        existing_user_id = get_jwt_identity()
        existing_user = db.session.get(TutorLegal, int(existing_user_id))
         if not existing_user:
                 return jsonify({"msg": "Usuario no encontrado"}), 400
        return jsonify(existing_user.serialize()), 200


                                                                       #use una ruta de registro para probar el login (por eso está comentada)


@api.route('tutorlegal/registro', methods=['POST'])
def registro_tutorlegal():


        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        rol_id = data.get('rol_id')
        telephone = data.get('telephone')
        password = data.get('password')

         if  not email or not password or not rol_id or not name or not telephone:
                 return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400

        existing_user = db.session.execute(select(TutorLegal).where(TutorLegal.email == email)).scalar_one_or_none()

         if existing_user:
                 return jsonify({'msg': 'Un perfil de administrador con este correo electrócnico ya existe'}), 409



        new_user = TutorLegal(email= email, rol_id= rol_id, password= password, name=name, telephone= telephone)
        new_user.set_password(password)


        db.session.add(new_user)
        db.session.commit()

         return jsonify({'msg': 'El perfil de administrador ha sido creado satisfactoriamente'}), 200


# ESTOS ENDPOINTS ESTAN COMENTADOS PORQUE AUN NO LOS HE COMPROBADO EN POSTMAN
# @api.route('calificaciones/crear', methods=['POST'])
# @jwt_required()
# def crear_calificaciones():
#     existing_user_id= get_jwt_identity()
#     existing_user= db.session.get(Profesor,int(existing_user_id))

#     if not existing_user:
#         return jsonify({"msg":"Usuario no autorizado"}),401

#     data= request.get_json()

#     if not data:
#         return jsonify({"msg":"Datos Inválidos"}),400

#     estudiante_id= data.get("estudiante_id")
#     estudiante= db.session.get(Estudiantes,estudiante_id)

#     if not estudiante:
#         return jsonify({"msg": "Estudiante no encontrado"}), 404

#     if estudiante.profesor_id != existing_user_id:
#         return jsonify ({"msg": "Este estudiante no es tuyo, no puedes modificarlo"}), 404


#     nueva_calificacion= Calificaciones(
#         calificacion= data.get("calificacion"),
#         estudiante_id=data.get("estudiante_id"),
#         asignatura_id=data.get("asignatura_id")
#     )

#     db.session.add(nueva_calificacion)
#     db.session.commit()

#     return jsonify(nueva_calificacion.serialize()),201


# @api.route('calificaciones/editar/<int:calificacion_id>', methods=['PUT'])
# @jwt_required()
# def editar_calificaciones(calificacion_id):
#     existing_user_id= get_jwt_identity()
#     existing_user = db.session.get(Calificaciones,int(existing_user_id))
#     if not existing_user:
#         return jsonify({'msg':'Usuario no autorizado'}),400

#     calificacion= db.session.get(Calificaciones, calificacion_id)

#     if not calificacion:
#         return jsonify({'msg':'Calificaion no encontrada'}),404

#     data= request.get_json()

#     if "calificacion" in data:
#         calificacion.calificacion_id= data["calificacion"]

#     if "estudiante_id" in data:
#         calificacion.estudiante_id=data["estudiante_id"]

#     if "asignatura_id" in data:
#         calificacion.asignatura_id=data["asignatura_id"]

#     db.session.commit()

#     return jsonify(calificacion.serialize()),200


# @api.route('calificaciones/eliminar/<int:calificacion_id>', methods=['DELETE'])
# @jwt_required()
# def eliminar_calificaciones(calificacion_id):
#      existing_user_id= get_jwt_identity()
#      existing_user = db.session.get(Calificaciones,int(existing_user_id))

#      if not existing_user:
#         return jsonify({'msg':'Usuario no autorizado'}),400

#      calificacion= db.session.get(Calificaciones, calificacion_id)

#      if not calificacion:
#         return jsonify({'msg':'Calificaion no encontrada'}),404

#      db.session.delete(calificacion)
#      db.session.commit()

#      return jsonify({"msg":"la calificación ha sido eliminada exitosamente"}),200