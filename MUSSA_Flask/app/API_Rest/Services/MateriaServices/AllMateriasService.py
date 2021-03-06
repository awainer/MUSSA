from app.API_Rest.codes import *
from app.models.generadorJSON.carreras_generadorJSON import generarJSON_materia
from app.models.filtros.carreras_filter import filtrar_materia
from app.API_Rest.Services.BaseService import BaseService
from app.models.carreras_models import Carrera
from app.utils import sustituir_todos_los_acentos


class AllMateriasService(BaseService):
    def getNombreClaseServicio(self):
        return "All Materias Service"

    def get(self):
        self.logg_parametros_recibidos()

        codigo_materia = self.obtener_parametro("codigo")
        nombre = self.obtener_texto("nombre")
        ids_carreras = self.obtener_lista("ids_carreras")
        palabras_clave = self.obtener_lista("palabras_clave")

        parametros_son_validos, msj, codigo = self.validar_parametros(dict([
            ("codigo", {
                self.PARAMETRO: codigo_materia,
                self.ES_OBLIGATORIO: False,
                self.FUNCIONES_VALIDACION: [
                    (self.es_numero_valido, [])
                ]
            }),
            ("nombre", {
                self.PARAMETRO: nombre,
                self.ES_OBLIGATORIO: False,
                self.FUNCIONES_VALIDACION: [
                    (self.validar_contenido_y_longitud_texto, [1, 50])
                ]
            }),
            self.get_validaciones_entidad_basica('ids_carreras', ids_carreras, Carrera, False)
        ]))

        if not parametros_son_validos:
            self.logg_error(msj)
            return {'Error': msj}, codigo

        filtros = {}
        if codigo_materia: filtros["codigo"] = codigo_materia
        if nombre: filtros["nombre"] = sustituir_todos_los_acentos(nombre)
        if ids_carreras: filtros["ids_carreras"] = ids_carreras
        if palabras_clave: filtros["palabras_clave"] = palabras_clave

        materias_result = []
        for materia in filtrar_materia(filtros):
            materias_result.append(generarJSON_materia(materia))

        MAX_LONGITUD_CODIGO = 4
        materias_result.sort(
            key=lambda materia_i: ((MAX_LONGITUD_CODIGO - len(materia_i["codigo"])) * "0" + materia_i["codigo"]),
            reverse=False
        )

        result = ({'materias': materias_result}, SUCCESS_OK)
        self.logg_resultado(result)

        return result


#########################################
CLASE = AllMateriasService
URLS_SERVICIOS = (
    '/api/materia/all',
)
#########################################
