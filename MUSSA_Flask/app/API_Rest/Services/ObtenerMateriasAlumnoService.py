from flask_restful import Resource
from app.API_Rest.codes import *
from flask import request

from flask_user import current_user, login_required

from app.models.alumno_models import Alumno, MateriasAlumno
from app.models.horarios_models import Curso
from app.models.carreras_models import Carrera, Materia
from app.models.docentes_models import CursosDocente, Docente
from app.DAO.MateriasDAO import *

import logging

import functools


class ObtenerMateriasAlumno(Resource):
    @login_required
    def get(self):
        args = request.args
        logging.info('Se invoco al servicio Obtener Materias Alumno con los siguientes parametros: {}'.format(args))

        alumno = Alumno.query.filter_by(user_id=current_user.id).first()

        if not self.argumentos_son_validos(args, alumno):
            result = ({'ERROR': 'Uno o más parámetros son inválidos'}, CLIENT_ERROR_BAD_REQUEST)
            logging.info('Obtener Materias Alumno devuelve como resultado: {}'.format(result))
            return result

        estados = self.obtener_ids_estados(args)

        id_materia_alumno = args["id_materia_alumno"] if "id_materia_alumno" in args else None

        query = MateriasAlumno.query.filter_by(alumno_id=alumno.id)

        if id_materia_alumno:
            query = query.filter_by(id=id_materia_alumno)

        if estados:
            query = query.filter(MateriasAlumno.estado_id.in_(estados))

        materias = query.all()

        materias_result = []
        for materia_alumno in materias:
            materia_carrera = Materia.query.filter_by(id=materia_alumno.materia_id).first()
            carrera = Carrera.query.filter_by(id=materia_alumno.carrera_id).first()
            estado = EstadoMateria.query.filter_by(id=materia_alumno.estado_id).first().estado

            calificacion = materia_alumno.calificacion if materia_alumno.calificacion else "-"

            fecha_aprobacion = "-"
            if materia_alumno.fecha_aprobacion:
                anio, mes, dia = str(materia_alumno.fecha_aprobacion).split(" ")[0].split("-")
                fecha_aprobacion = "{}/{}/{}".format(dia, mes, anio)

            aprobacion_cursada = "-"
            if (materia_alumno.cuatrimestre_aprobacion_cursada and
                    materia_alumno.anio_aprobacion_cursada):
                aprobacion_cursada = materia_alumno.cuatrimestre_aprobacion_cursada + "C / "
                aprobacion_cursada += materia_alumno.anio_aprobacion_cursada

            acta_o_resolucion = materia_alumno.acta_o_resolucion if materia_alumno.acta_o_resolucion else "-"

            forma_aprobacion_materia = "-"
            if materia_alumno.forma_aprobacion_id:
                query = FormaAprobacionMateria.query.filter_by(id=materia_alumno.forma_aprobacion_id)
                forma_aprobacion_materia = query.first().forma

            curso = "Sin designar"
            if materia_alumno.curso_id:
                curso_elegido = Curso.query.filter_by(id=materia_alumno.curso_id).first()
                docentes = ""
                for curso_docente in CursosDocente.query.filter_by(curso_id=curso_elegido.id).all():
                    docente = Docente.query.filter_by(id=curso_docente.docente_id).first()
                    docentes += docente.obtener_nombre_completo() + "-"
                curso = "{}: {}".format(curso_elegido.codigo, docentes[:-1])

            materias_result.append({
                'id': materia_alumno.id,
                'id_materia': materia_carrera.id,
                'codigo': materia_carrera.codigo,
                'nombre': materia_carrera.nombre,
                'id_carrera': carrera.id,
                'id_curso': materia_alumno.curso_id if materia_alumno.curso_id else '-1',
                'carrera': carrera.nombre + " (" + carrera.plan + ")",
                'curso': curso,
                'estado': estado,
                'aprobacion_cursada': aprobacion_cursada,
                'calificacion': calificacion,
                'fecha_aprobacion': fecha_aprobacion,
                'acta_o_resolucion': acta_o_resolucion,
                'forma_aprobacion_materia': forma_aprobacion_materia
            })

        materias_result = sorted(materias_result, key=functools.cmp_to_key(cmp_materias_result))
        result = ({'materias': materias_result}, SUCCESS_OK)
        logging.info('Obtener Materias Alumno devuelve como resultado: {}'.format(result))

        return result

    def argumentos_son_validos(self, args, alumno):
        return self.id_es_valido(args, alumno) and self.estados_son_validos(args)

    def id_es_valido(self, args, alumno):
        id_materia_alumno = args["id_materia_alumno"] if "id_materia_alumno" in args else None
        if not id_materia_alumno:
            return True

        return (id_materia_alumno.isdigit() and
                len(MateriasAlumno.query.filter_by(alumno_id=alumno.id).filter_by(id=id_materia_alumno).all()) > 0)

    def estados_son_validos(self, args):
        try:
            estados = args["estados"].split(";") if "estados" in args else []
            for cod_estado in estados:
                texto = ESTADO_MATERIA[int(cod_estado)]
                estado = EstadoMateria.query.filter_by(estado=texto).first()
                assert (estado is not None)
        except:
            return False

        return True

    def obtener_ids_estados(self, args):
        ids_estados = []

        estados = args["estados"].split(";") if "estados" in args else []
        for cod_estado in estados:
            texto = ESTADO_MATERIA[int(cod_estado)]
            estado = EstadoMateria.query.filter_by(estado=texto).first()
            ids_estados.append(estado.id)

        return ids_estados


def cmp_materias_result(materia1, materia2):
    codigo1 = convertir_codigo(materia1)
    codigo2 = convertir_codigo(materia2)

    if codigo1 < codigo2:
        return -1
    elif codigo1 > codigo2:
        return 1
    return 0


def convertir_codigo(materia):
    LONGITUD_CODIGO = 4
    codigo = materia["codigo"]
    return "0" * (LONGITUD_CODIGO - len(codigo)) + codigo