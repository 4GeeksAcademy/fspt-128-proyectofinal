"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, Profesor, SuperAdmin, TutorLegal, Calificaciones,Estudiantes
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from sqlalchemy import select
from flask_jwt_extended import create_access_token , get_jwt_identity,jwt_required
from flask_bcrypt import generate_password_hash,check_password_hash


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

#el rol debe agregarse al modelo del profesor 
@api.route('/superadmin/registro', methods=['POST'])
def registro_superadmin():
    data= request.get_json()
    email= data.get('email')
    rol_id= data.get('rol_id')
    password= data.get('password')
    nombre_colegio = data.get('nombre_colegio')

    if  not email or not password or not rol_id or not nombre_colegio:
        return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400
    
    existing_user= db.session.execute(select(SuperAdmin).where(SuperAdmin.email == email)).scalar_one_or_none()

    if existing_user:
        return jsonify ({'msg': 'Un perfil de administrador con este correo electrócnico ya existe'}),409
    

    new_user= SuperAdmin(email= email, rol_id= rol_id,password= password, nombre_colegio= nombre_colegio)
    new_user.set_password(password)
    

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'El perfil de administrador ha sido creado satisfactoriamente'}), 200



@api.route('/superadmin/login', methods=['POST'])
def login_superadmin():
    data= request.get_json()
    email= data.get('email')
    password= data.get('password')


    if  not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400
    
    existing_user= db.session.execute(select(SuperAdmin).where(SuperAdmin.email == email)).scalar_one_or_none()

    if existing_user is None:
        return jsonify ({'msg':'El correo eletrócnico o contraseña son incorrectos'}),401
    
    if existing_user.check_password(password):
         access_token = create_access_token(identity=str(existing_user.id))
         return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}),200
    
    else: 
        return jsonify({'msg':'El correo eletrócnico o contraseña son incorrectos'}), 401
    

@api.route('perfil/superadmin', methods=['GET'])
@jwt_required()
def perfil_superadmin():
    existing_user_id= get_jwt_identity()
    existing_user = db.session.get(SuperAdmin,int(existing_user_id))
    if not existing_user:
        return jsonify({"msg":"Usuario no encontrado"}),400
    return jsonify(existing_user.serialize()),200




@api.route('profesor/login',methods=['POST'])
def login_profesor():
     data= request.get_json()
     email= data.get('email')
     password= data.get('password')

     if  not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400
    
     existing_user= db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

     if existing_user is None:
        return jsonify ({'msg':'El correo eletrócnico o contraseña son incorrectos'}),401
    
     if existing_user.check_password(password):
         access_token = create_access_token(identity=str(existing_user.id))
         return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}),200
    
     else: 
        return jsonify({'msg':'El correo eletrócnico o contraseña son incorrectos'}), 401
     

@api.route('perfil/profesor', methods=['GET'])
@jwt_required()
def perfil_profesor():
    existing_user_id= get_jwt_identity()
    existing_user = db.session.get(Profesor,int(existing_user_id))
    if not existing_user:
        return jsonify({"msg":"Usuario no encontrado"}),400
    return jsonify(existing_user.serialize()),200


@api.route('calificaciones/crear', methods=['POST'])
@jwt_required()
def crear_calificaciones():
    existing_user_id= get_jwt_identity()
    existing_user= db.session.get(Profesor,int(existing_user_id))

    if not existing_user:
        return jsonify({"msg":"Usuario no autorizado"}),401
    
    data= request.get_json()

    if not data:
        return jsonify({"msg":"Datos Inválidos"}),400
    
    estudiante_id= data.get("estudiante_id")
    estudiante= db.session.get(Estudiantes,estudiante_id)

    if not estudiante:
        return jsonify({"msg": "Estudiante no encontrado"}), 404
    
    if estudiante.existing_user_id != existing_user:
        return jsonify ({"msg": "Este estudiante no es tuyo, no puedes modificarlo"}), 404
        
    
    nueva_calificacion= Calificaciones(
        calificacion= data.get("calificacion"),
        estudiante_id=data.get("estudiante_id"),
        asignatura_id=data.get("asignatura_id")
    )

    db.session.add(nueva_calificacion)
    db.session.commit()

    return jsonify(nueva_calificacion.serialize()),201




@api.route('calificaciones/editar/<int:calificacion_id>', methods=['PUT'])
@jwt_required()
def editar_calificaciones(calificacion_id):
    existing_user_id= get_jwt_identity()
    existing_user = db.session.get(Calificaciones,int(existing_user_id))
    if not existing_user:
        return jsonify({'msg':'Usuario no autorizado'}),400
    
    calificacion= db.session.get(Calificaciones, calificacion_id)

    if not calificacion:
        return jsonify({'msg':'Calificaion no encontrada'}),404
    
    data= request.get_json()

    if "calificacion" in data:
        calificacion.calificacion_id= data["calificacion"]

    if "estudiante_id" in data:
        calificacion.estudiante_id=data["estudiante_id"]

    if "asignatura_id" in data:
        calificacion.asignatura_id=data["asignatura_id"]

    db.session.commit()

    return jsonify(calificacion.serialize()),200


@api.route('calificaciones/eliminar/<int:calificacion_id>', methods=['DELETE'])
@jwt_required()
def eliminar_calificaciones(calificacion_id):
     existing_user_id= get_jwt_identity()
     existing_user = db.session.get(Calificaciones,int(existing_user_id))

     if not existing_user:
        return jsonify({'msg':'Usuario no autorizado'}),400
    
     calificacion= db.session.get(Calificaciones, calificacion_id)

     if not calificacion:
        return jsonify({'msg':'Calificaion no encontrada'}),404
    
     db.session.delete(calificacion)
     db.session.commit()

     return jsonify({"msg":"la calificación ha sido eliminada exitosamente"}),200

    



@api.route('tutorlegal/login',methods=['POST'])
def login_tutor_legal():
    data= request.get_json()
    email= data.get('email')
    password= data.get('password')

    if  not email or not password:
        return jsonify({'msg': 'El correo electrónico y contraseña son requeridos'}), 400
    
    existing_user= db.session.execute(select(TutorLegal).where(TutorLegal.email == email)).scalar_one_or_none()

    if existing_user is None:
        return jsonify ({'msg':'El correo eletrócnico o contraseña son incorrectos'}),401
    
    if existing_user.check_password(password):
         access_token = create_access_token(identity=str(existing_user.id))
         return jsonify({'msg': 'Inicio de sesión exitoso', 'token': access_token, 'existing_user': existing_user.serialize()}),200
    
    else: 
        return jsonify({'msg':'El correo eletrócnico o contraseña son incorrectos'}), 401


@api.route('perfil/tutorlegal', methods=['GET'])
@jwt_required()
def perfil_tutorlegal():
    existing_user_id= get_jwt_identity()
    existing_user = db.session.get(TutorLegal,int(existing_user_id))
    if not existing_user:
        return jsonify({"msg":"Usuario no encontrado"}),400
    return jsonify(existing_user.serialize()),200

    


    #use una ruta de registro para probar el login (por eso está comentada)
@api.route('profesor/registro', methods=['POST'])
def registro_tutorlegal():
    data= request.get_json()
    name=data.get('name')
    email= data.get('email')
    rol_id= data.get('rol_id')
    telephone= data.get('telephone')
    password= data.get('password')
  

    if  not email or not password or not rol_id or not name or not telephone:
        return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400
    
    existing_user= db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

    if existing_user:
        return jsonify ({'msg': 'Un perfil de administrador con este correo electrócnico ya existe'}),409
    

    new_user= Profesor(email= email, rol_id= rol_id,password= password,name=name, telephone= telephone)
    new_user.set_password(password)
    

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'El perfil de administrador ha sido creado satisfactoriamente'}), 200