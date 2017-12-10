from flask_restful import Resource
from app.API_Rest.codes import *
from flask import request

from app.models.horarios_models import Horario, Curso, CarreraPorCurso, HorarioPorCurso
from app.models.carreras_models import Carrera, Materia
from app.models.docentes_models import Docente, CursosDocente

import logging

class BuscarCursos(Resource):
    def get(self):
        args = request.args
        logging.info('Se invoco al servicio Buscar Cursos con los siguientes parametros: {}'.format(args))

        q_id_curso = args["id_curso"] if "id_curso" in args else None
        q_nombre_curso = args["nombre_curso"] if "nombre_curso" in args else None
        q_codigo_materia = args["codigo_materia"] if "codigo_materia" in args else None
        q_carrera = args["id_carrera"] if "id_carrera" in args else None
        filtrar_cursos = self.obtener_valor_filtrar_cursos(args)

        if not self.parametros_son_validos(q_id_curso, q_nombre_curso, q_codigo_materia, q_carrera, filtrar_cursos):
            logging.error('El servicio Buscar Cursos recibió parámetros inválidos')
            return {'Error': 'Este servicio recibió parámetros inválidos'}, CLIENT_ERROR_BAD_REQUEST

        query = Curso.query

        if q_id_curso:
            query = query.filter_by(id=q_id_curso)
        else:
            if q_nombre_curso: query = query.filter(Curso.codigo.like("%" + q_nombre_curso + "%"))
            if q_codigo_materia: query = query.filter(Curso.codigo_materia.like(q_codigo_materia + "%"))

        if filtrar_cursos:
            query = query.filter((Curso.se_dicta_primer_cuatrimestre == True) | (Curso.se_dicta_segundo_cuatrimestre == True))
    
        cursos = query.all()

        cursos_result = []
        for curso in cursos:

            carreras_response = []
            query = CarreraPorCurso.query.filter_by(curso_id=curso.id)
            if q_carrera: query = query.filter_by(carrera_id=q_carrera)
            carrerasPorCurso = query.all()

            for carrera in carrerasPorCurso:
                carrera_db = Carrera.query.filter_by(id=carrera.carrera_id).first()
                carreras_response.append({
                    'codigo': carrera_db.codigo,
                    'nombre': carrera_db.nombre
                })

            if not carreras_response: #No es un curso valido para la query elegida
                continue

            horarios_response = []
            horarios_por_curso = HorarioPorCurso.query.filter_by(curso_id=curso.id).all()
            for horario in horarios_por_curso:
                horario_db = Horario.query.filter_by(id=horario.horario_id).first()
                horarios_response.append({
                    'dia': horario_db.dia,
                    'hora_desde': self.convertir_hora(horario_db.hora_desde),
                    'hora_hasta': self.convertir_hora(horario_db.hora_hasta) 
                })

            docentes = ""
            docentes_del_curso = CursosDocente.query.filter_by(curso_id=curso.id).all()
            for doc in docentes_del_curso:
                docentes += Docente.query.filter_by(id=doc.docente_id).first().obtener_nombre_completo() + "-"
            docentes = docentes[:-1]

            cursos_result.append({
                'id': curso.id,
                'codigo_curso': curso.codigo,
                'codigo_materia': curso.codigo_materia,
                'se_dicta_primer_cuatri': curso.se_dicta_primer_cuatrimestre,
                'se_dicta_segundo_cuatri': curso.se_dicta_segundo_cuatrimestre,
                'cuatrimestre': self.mensaje_cuatrimestre(curso),
                'carreras': carreras_response,
                'horarios': horarios_response,
                'docentes': docentes,
                'puntaje': self.calcular_puntaje(curso)
            })

        cursos_result.sort(key=lambda curso : curso["puntaje"], reverse=True)

        result = ({'cursos': cursos_result}, SUCCESS_OK)
        logging.info('Buscar Cursos devuelve como resultado: {}'.format(result))

        return result


    def obtener_valor_filtrar_cursos(self, args):
        if not "filtrar_cursos" in args:
            return True

        filtrar = args["filtrar_cursos"].lower()
        return (filtrar != "false")


    def calcular_puntaje(self, curso):
        if curso.cantidad_encuestas_completas == 0:
            return 0
        return (curso.puntaje_total_encuestas / curso.cantidad_encuestas_completas)


    def convertir_hora(self, horario):
        l_horario = str(horario).split(".")
        hora = l_horario[0]

        if (0 <= int(hora) < 10):
            hora = "0" + hora

        if len(l_horario) == 1:
            return hora + ":00"
        return hora + ":30"


    def mensaje_cuatrimestre(slef, curso):
        if not curso.se_dicta_primer_cuatrimestre and not curso.se_dicta_segundo_cuatrimestre:
            return "No se dicta actualmente"
        if curso.se_dicta_primer_cuatrimestre and curso.se_dicta_segundo_cuatrimestre:
            return "Ambos cuatrimestres"
        if curso.se_dicta_primer_cuatrimestre:
            return "Solo el 1º cuatrimestre"
        return "Solo el 2º cuatrimestre"


    def parametros_son_validos(self, q_id_curso, q_nombre_curso, q_codigo_materia,
                                q_carrera, filtrar_cursos):
        return (self.id_curso_es_valido(q_id_curso, filtrar_cursos)
                and self.nombre_curso_es_valido(q_nombre_curso)
                and self.codigo_materia_es_valido(q_codigo_materia)
                and self.carrera_es_valida(q_carrera))


    def id_curso_es_valido(self, id_curso, filtrar_cursos):
        if not id_curso:
            return True

        id_curso = str(id_curso)

        query = Curso.query.filter_by(id=id_curso)
        if filtrar_cursos:
            query = query.filter((Curso.se_dicta_primer_cuatrimestre == True) | (Curso.se_dicta_segundo_cuatrimestre == True))

        return (self.esta_formado_solo_por_numeros(id_curso) and len(query.all()) > 0)


    def nombre_curso_es_valido(self, nombre):
        if not nombre:
            return True

        for letra in nombre:
            if not letra.isdigit() and not letra.isalpha() and not letra in ["-", "_", ":", "'"]:
                return False
        return True


    def codigo_materia_es_valido(self, codigo):
        if not codigo:
            return True

        codigo = str(codigo)
        if len(codigo) < 2 or len(codigo) > 4:
            return False

        return self.esta_formado_solo_por_numeros(codigo)


    def carrera_es_valida(self, carrera):
        if not carrera:
            return True

        carrera = str(carrera)
        return (self.esta_formado_solo_por_numeros(carrera) and
                len(Carrera.query.filter_by(id=carrera).all()) > 0)


    def esta_formado_solo_por_numeros(self, cadena):
        for letra in cadena:
            if not letra.isdigit():
                return False
        return True