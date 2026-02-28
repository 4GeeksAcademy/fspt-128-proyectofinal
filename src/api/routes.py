"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, Profesor
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from sqlalchemy import select

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
@api.route('/profesor/registro', methods=['POST'])
def registro_profesor():
    data= request.get_json()
    name= data.get('name')
    email= data.get('email')
    telephone= data.get('telephone')
    role_id= data.get('role_id')
    password= data.get('password')

    if not name or not email or not telephone or not password or not role_id:
        return jsonify({'msg': 'Por favor completar todos los campos para completar el registro'}), 400
    
    existing_professor = db.session.execute(select(Profesor).where(Profesor.email == email)).scalar_one_or_none()

    if existing_professor:
        return jsonify ({'msg': 'El profesor con este correo electrócnico ya exite'}),409
    

    new_professor= Profesor(name= name, email= email, telephone= telephone, role_id= role_id,)
    new_professor.set_password(password)

    db.session.add(new_professor)
    db.session.commit()

    return jsonify({'msg': 'El perfil del profesor ha sido creado satisfactoriamente'}), 201
