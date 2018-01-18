from flask_restful import Resource
from app.API_Rest.codes import *
from flask import request
from app.models.horarios_models import Curso
from app.models.carreras_models import Carrera, Materia
from flask_user import current_user, login_required
from app.models.alumno_models import Alumno, MateriasAlumno
from app.models.respuestas_encuesta_models import EncuestaAlumno
from app.models.generadorJSON.carreras_generadorJSON import generarJSON_carrera, generarJSON_materia
from app.models.generadorJSON.horarios_generadorJSON import generarJSON_curso

import logging


class ObtenerEncuestasAlumno(Resource):
    @login_required
    def get(self):
        args = request.args
        logging.info('Se invoco al servicio Obtener Encuesta Alumno con los siguientes parametros: {}'.format(args))

        id_encuesta = args["id_encuesta"] if "id_encuesta" in args else None

        if not self.finalizada_es_valido(args) or not self.id_encuesta_es_valido(id_encuesta):
            logging.error('El servicio Obtener Encuestas Alumno ecibió uno o más parámetros inválidos')
            return {'Error': 'Este servicio recibió uno o más parámetros inválidos'}, CLIENT_ERROR_BAD_REQUEST

        alumno = Alumno.query.filter_by(user_id=current_user.id).first()

        encuestas = []
        if alumno:
            query = EncuestaAlumno.query.filter_by(alumno_id=alumno.id)

            if id_encuesta:
                query = query.filter_by(id=id_encuesta)

            if "finalizadas" in args:
                query = query.filter_by(finalizada=self.obtener_parametro_finalizadas(args))

            encuestas = query.all()

        encuestas_result = []
        for encuesta in encuestas:
            materiaAlumno = MateriasAlumno.query.get(encuesta.materia_alumno_id)
            carrera = Carrera.query.get(materiaAlumno.carrera_id)
            curso = Curso.query.get(materiaAlumno.curso_id)
            materia = Materia.query.get(materiaAlumno.materia_id)

            encuestas_result.append({
                "id": encuesta.id,
                "alumno_id": encuesta.alumno_id,
                "materia_alumno_id": encuesta.materia_alumno_id,
                "carrera": generarJSON_carrera(carrera),
                "materia": generarJSON_materia(materia),
                "curso": generarJSON_curso(curso),
                "cuatrimestre_aprobacion_cursada": encuesta.cuatrimestre_aprobacion_cursada,
                "anio_aprobacion_cursada": encuesta.anio_aprobacion_cursada,
                "fecha_aprobacion": "{}C / {}".format(encuesta.cuatrimestre_aprobacion_cursada,
                                                      encuesta.anio_aprobacion_cursada),
                "finalizada": encuesta.finalizada
            })

        result = ({'encuestas': encuestas_result}, SUCCESS_OK)
        logging.info('Obtener Encuestas Alumno devuelve como resultado: {}'.format(result))

        return result

    def obtener_parametro_finalizadas(self, args):
        finalizadas = args["finalizadas"].upper()
        return finalizadas == "TRUE"

    def finalizada_es_valido(self, args):
        if not "finalizadas" in args:
            return True

        finalizadas = args["finalizadas"].upper()
        return (finalizadas == "TRUE" or finalizadas == "FALSE")

    def id_encuesta_es_valido(self, id_encuesta):
        if not id_encuesta:
            return True

        return (id_encuesta.isdigit() and EncuestaAlumno.query.filter_by(id=id_encuesta).first())
