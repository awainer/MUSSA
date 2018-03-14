if __name__ == "__main__":
    import sys

    sys.path.append("../..")

from app.API_Rest.GeneradorPlanCarreras.my_utils import get_str_cuatrimestre
from tests.TestResolucionPlanDeEstudios.TestConHorariosPDFSeparadosEnCuatrimestres import \
    TestConHorariosPDFSeparadosEnCuatrimestres


class Test_plan_licenciatura_con_horarios_cargados_desde_pdf_fiuba_con_cuatrimestres_separados_comenzando_el_segundo_cuatrimestre(
    TestConHorariosPDFSeparadosEnCuatrimestres):
    def get_nombre_test(self):
        return "test_plan_licenciatura_con_horarios_cargados_desde_pdf_fiuba_con_cuatrimestres_separados_comenzando_el_segundo_cuatrimestre"

    def get_materias_test(self):
        return self.materias

    def get_horarios_test(self):
        return self.horarios

    def get_creditos_minimos_electivas(self):
        return 40

    def get_maxima_cantidad_cuatrimestres(self):
        return 18  # Plan tiene 4,5 años == 9 cuatrimestres. Puede llevar hasta el doble: 18

    def get_maxima_cantidad_materias_por_cuatrimestre(self):
        return 4

    def comienza_en_primer_cuatrimestre(self):
        return False

    #################################################################
    ##                  Verificacion de resultados                 ##
    #################################################################

    def verificar_resultados(self, parametros, resultados):
        self.todas_las_materias_obligatorias_se_hacen(parametros, resultados)
        self.los_cuatrimestres_de_las_correlativas_son_menores(parametros, resultados)
        self.los_creditos_en_electivas_cumplen_con_el_minimo(parametros, resultados)
        self.no_se_elige_un_horario_no_disponible_ese_cuatrimestre(parametros, resultados)


if __name__ == "__main__":
    test_a_ejecutar = Test_plan_licenciatura_con_horarios_cargados_desde_pdf_fiuba_con_cuatrimestres_separados_comenzando_el_segundo_cuatrimestre()
    test_a_ejecutar.ejecutar_test()
