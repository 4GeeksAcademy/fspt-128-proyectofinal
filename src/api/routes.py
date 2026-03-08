"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import select
from flask_cors import CORS
from api.utils import generate_sitemap, APIException
from api.models import db, Profesor, TutorLegal, Estudiantes, Aula, Eventos, SuperAdmin, Asignaturas
from flask import Flask, request, jsonify, url_for, Blueprint


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
# def tutorLegal_required():
#     user_id = get_jwt_identity()
#     user = TutorLegal.query.get(user_id)
#     if not user or user.rol_id != 3:
#         return jsonify({"msg": "Solo tutor legal"}), 403
#     return None

# SUPERADMIN REGISTRO, LOGIN Y GET#


@api.route('/superadmin/registro', methods=['POST'])
def registro_superadmin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nombre_colegio = data.get('nombre_colegio')

    if not email or not password  or not nombre_colegio:
        return jsonify({'msg': 'Por favor completar todos los campos'}), 400

    existing_user = db.session.execute(select(SuperAdmin).where(
        SuperAdmin.email == email)).scalar_one_or_none()

    if existing_user:
        return jsonify({'msg': 'Ya existe un administrador con este correo'}), 409

    new_user = SuperAdmin(
        email=email,
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

    existing_user = db.session.execute(select(SuperAdmin).where(
        SuperAdmin.email == email)).scalar_one_or_none()
    if existing_user is None:
        return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401

    if existing_user.check_password(password):
        access_token = create_access_token(identity=str(existing_user.id),
            additional_claims={  
                "rol_id": existing_user.rol_id,
                "email": existing_user.email,
                "nombre_colegio": existing_user.nombre_colegio
            }
        )
        return jsonify({'access_token': access_token}), 200
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


@api.route('/eventos/<int:id>', methods=['PUT'])
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


@api.route('/eventos/<int:id>', methods=['DELETE'])
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

########REGISTRO PROFESORES###########


@api.route('profesor/registro', methods=['POST'])
def registro_profesor():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    rol_id = data.get('rol_id')
    telephone = data.get('telephone')
    password = data.get('password')

    if not email or not password or not rol_id or not name or not telephone:
        return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400

    existing_user = db.session.execute(select(Profesor).where(
        Profesor.email == email)).scalar_one_or_none()

    if existing_user:
        return jsonify({'msg': 'Un perfil de profesor con este correo electrócnico ya existe'}), 409

    new_user = Profesor(email=email, rol_id=rol_id,
                        password=password, name=name, telephone=telephone)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'El perfil de profesor ha sido creado satisfactoriamente'}), 200

#####LOGIN DEL PROFESOR##########


@api.route('/profesor/login',methods=['POST'])
def login_profesor():
    profe_id= get_jwt_identity()
    claims= get_jwt()
    if claims["rol_id"] != 2:
        return jsonify({"msg": "Solo profesores"}), 403
   
    data= request.get_json()
    email= data.get('email')
    password= data.get('password')

    if not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400

    existing_user= db.session.get(Profesor, int(profe_id))

    

    if existing_user.check_password(password):
        access_token = create_access_token(
            identity=str(existing_user.id),
            additional_claims={
                "rol_id": existing_user.rol_id,
                "email": existing_user.email,
                "aula_id": Aula.aula_id,
                "clase": Aula.clase
            }
        )

        return jsonify({
            'msg': 'Inicio de sesión exitoso',
            'token': access_token,
            'existing_user': existing_user.serialize()
        }), 200

    return jsonify({'msg': 'Correo o contraseña incorrectos'}), 401                                                                                                                                                                                               

########OBTENER EL LISTADO DE PROFESORES Y SU INFO

@api.route('/profesores', methods=['GET'])
@jwt_required()
def perfil_profesor():
    existing_user_id = get_jwt_identity()
    existing_user = db.session.get(Profesor, int(existing_user_id))
    if not existing_user:
        return jsonify({"msg": "Usuario no encontrado"}), 400
    return jsonify(existing_user.serialize()), 200

#########MODIFICAR PROFESOR SE PUDEN MODIFICAR ALL MENOS EL ID Y EL ROL_ID PORQUE SI NO SE PUEDEN HACER COSAS RARAS COMO CAMBIAR DE PROFESOR A SUPERADMIN O COSAS ASI############
@api.route('/profesor/<int:id>', methods=['PUT'])
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

########ELIMINAR PROFESOR############
@api.route('/profesor/<int:id>', methods=['DELETE'])
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


@api.route('/estudiantes', methods=['POST'])
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


@api.route('/estudiantes/<int:id>', methods=['DELETE'])
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



######## PARA CREAR AULA SE DEBE ASIGNAR UN CURSO, UNA CLASE Y EL NOMBRE_COLEGIO AL QUE PERTENECE,ADEMAS SE DEBE ASIGNAR UN CURSO Y UNA CLASE PARA IDENTIFICAR EL AULA, POR EJEMPLO CURSO: 1 Y CLASE: A SERIA EL AULA 1A DEL COLEGIO DEL SUPERADMIN QUE HACE LA PETICION############

@api.route('/crear/aula', methods=['POST'])
@jwt_required()

def crear_aula():
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    
    data = request.json    
    classroom = Aula(
        curso=data.get("curso"),
        clase=data.get("clase"),
        colegio_id= data.get("SuperAdmin.nombre_colegio")
    )
    if classroom.curso is None or classroom.clase is None:
        return jsonify({"msg": "Curso, clase y colegio_id son requeridos para crear un aula"}), 400
    
    db.session.add(classroom)
    db.session.commit()
    return jsonify(classroom.serialize()), 201

#########ELIMINAR AULA################# SE DEBE ESPECIFICAREL ID Y EL NOMBRE DE LA CLASE PARA ELIMINAR UN AULA, ADEMAS SE DEBE VERIFICAR QUE EL AULA ESTE VACIA, ES DECIR QUE NO TENGA PROFESOR ASIGNADO NI ESTUDIANTES INSCRITOS, SI EL AULA TIENE PROFESOR O ESTUDIANTES NO SE PERMITIRA LA ELIMINACION Y SE MOSTRARA UN MENSAJE DE ERROR INDICANDO QUE EL AULA DEBE ESTAR VACIA PARA SER ELIMINADA, ASI SE ASEGURA QUE NO SE ELIMINEN AULAS QUE ESTEN EN USO Y SE PIERDAN LOS DATOS DE LOS PROFESORES Y ESTUDIANTES ASIGNADOS A ESE AULA############

@api.route('/eliminar/aula/<int:id>/<string:clase>', methods=['DELETE'])
@jwt_required()
def eliminar_aula(id, clase):
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
   
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
  
    db.session.delete(aula)
    db.session.commit()
    return jsonify({"msg": f"Aula '{clase}' (ID: {id}) eliminada con éxito"}), 200
    

#####OBTENER AULAS################# NO TIENE JWT PORQUE LO PODRAN VER LOS 3 ROLES. 

@api.route('/aulas', methods=['GET'])
def obtener_aulas():
 
    aulas = Aula.query.all()
    return jsonify([aula.serialize() for aula in aulas]), 200


#########MODIFICAR AULA AQUI SE PUEDE CAMBIAR LOS DATOS DEL AULA ############

@api.route('/aula/<int:id>', methods=['PUT'])
@jwt_required()

def actualizar_aula(id):
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    admin_check = admin_required()
    if admin_check: 
        return admin_check
    
    aula = Aula.query.get(id)
    if not aula:
        return jsonify({"msg": "Aula no encontrada"}), 404
        
    data = request.get_json()
    aula.curso = data.get("curso", aula.curso)
    aula.clase = data.get("clase", aula.clase)


    db.session.commit()
    return jsonify({"msg": "Aula actualizada", "aula": aula.serialize()}), 200


#####CREAR ASIGNATURAS TRONCALES#########SOLO SUPERADMIN LAS PUEDE MODIFICAR,CREAR O ELIMINAR.

@api.route('/asignaturas', methods=['POST'])
@jwt_required()
def create_asignatura():
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    data = request.get_json()
    nueva = Asignaturas(nombre_asignatura=data.get('nombre_asignatura'))
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"msg": "Asignatura troncal creada"}), 201

####### MODIFICAR NOMBRE_ASIGNATURA ########
@api.route('/asignaturas/<int:id>', methods=['PUT'])
@jwt_required()
def update_asignatura(id):
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

   
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

######## BORRRAR ASIGNATURA####SOLO X ADMIN INDICANDO EL ID DE LA ASIGNATURA

@api.route('/asignaturas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asignatura(id):
    Sadmin_colegio= get_jwt_identity()
    claims= get_jwt()
    if claims["nombre_colegio"] != "SuperAdmin.nombre_colegio":
        return jsonify({"msg": "Solo administradores del colegio"}), 403
    exisisting_user = db.session.get(SuperAdmin, str(Sadmin_colegio))
    if not exisisting_user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    
    asignatura = db.session.get(Asignaturas, id)
    if not asignatura:
        return jsonify({"msg": "No existe"}), 404
    
    db.session.delete(asignatura)
    db.session.commit()
    return jsonify({"msg": "Asignatura eliminada globalmente"}), 200


########## OBTENER TODAS LAS ASIGNATURAS NO TIENE JWT LAS PUEDEN VER TODOS LOS ROLES######

@api.route('/asignaturas', methods=['GET'])

def get_asignaturas():
    
    result = db.session.execute(select(Asignaturas)).scalars().all()
    asignaturas_list = [asignatura.serialize() for asignatura in result]

    return jsonify(asignaturas_list), 200



####CREAR TUTOR LEGAL##################

@api.route('/tutoresLegales/', methods=['POST'])
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

##### MODIFICAR INFORMACION DE LOS TURORES LEGALES#########


@api.route('/tutoresLegales/<int:id>', methods=['PUT'])
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




######## LOGIN DE TUTORES LEGALES ###########

@api.route('tutorlegal/login', methods=['POST'])
def login_tutor_legal():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400
    existing_user = db.session.execute(select(TutorLegal).where(
        TutorLegal.email == email)).scalar_one_or_none()
    if existing_user is None:
        return jsonify({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401
    if existing_user.check_password(password):
        access_token = create_access_token(identity=str(existing_user.id))
        return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}), 200
    else:
        return jsonify({'msg': 'El correo eletrócnico o contraseña son incorrectos'}), 401

########## OBTENER PERFIL DE TUTOR LEGAL###########

@api.route('/perfil/tutorlegal', methods=['GET'])
@jwt_required()
def perfil_tutorlegal():
    existing_user_id = get_jwt_identity()
    existing_user = db.session.get(TutorLegal, int(existing_user_id))
    if not existing_user:
        return jsonify({"msg": "Usuario no encontrado"}), 400
    return jsonify(existing_user.serialize()), 200

#######REGISTRO TUTOR LEGAL SOLO SUPERADMIN LO HACE########

@api.route('tutorlegal/registro', methods=['POST'])
def registro_tutorlegal():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    rol_id = data.get('rol_id')
    telephone = data.get('telephone')
    password = data.get('password')
    if not email or not password or not rol_id or not name or not telephone:
        return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400
    existing_user = db.session.execute(select(TutorLegal).where(
        TutorLegal.email == email)).scalar_one_or_none()
    if existing_user:
        return jsonify({'msg': 'Un perfil de administrador con este correo electrócnico ya existe'}), 409
    new_user = TutorLegal(email=email, rol_id=rol_id,
                          password=password, name=name, telephone=telephone)
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
