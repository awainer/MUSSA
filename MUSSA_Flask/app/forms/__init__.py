from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms import validators


class AgregarDocente(FlaskForm):
    nombre = StringField(u'Nombre', validators=[validators.DataRequired(message='Este campo es obligatorio'),
                                                validators.Length(min=4, max=25)])
    apellido = StringField(u'Apellido', validators=[validators.optional()])

    enviar = SubmitField('Guardar', render_kw={'class': 'btn btn-mussa-default'})
    volver = SubmitField('Volver', render_kw={'class': 'btn btn-mussa-default'})

    carreras_disponibles = SelectField('Carrera', choices=[],
                                       render_kw={"onchange": "populate_materias(this.options[this.selectedIndex].id)"})
    materias_disponibles = SelectField('Materia', choices=[], render_kw={"disabled": "true",
                                                                         "onchange": "populate_cursos(this.options[this.selectedIndex].id)"})
    cursos_disponibles = SelectField('Curso', choices=[], render_kw={"disabled": "true"})

    tabla_materias_columnas = [
        {
            "field": "codigo",
            "title": "Codigo",
            "sortable": True,
        },
        {
            "field": "materia",
            "title": "Materia",
            "sortable": True,
        },
        {
            "field": "curso",
            "title": "Curso",
            "sortable": True,
        },
        {
            "field": "id_curso",
            "title": "Id del curso",
            "visible": False,
        },
        {
            "field": "id_carrera",
            "title": "Id de carrera",
            "visible": False,
        },
        {
            "field": "carrera",
            "title": "Carrera",
            "sortable": True,
        },
        {
            "field": "actions",
            "title": "Acciones",
            "sorteable": False
        }
    ]
