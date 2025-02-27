from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, InputRequired, URL, Optional, ValidationError


class ScanForm(FlaskForm):
    target_url = StringField('Target URL', validators=[InputRequired(), URL(message="URL invalida")])
    strength = SelectField('Set Strenght', choices = [('DEFAULT', 'Default'), ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('INSANE', 'Insane')], validators=[InputRequired()])
    schedule = BooleanField('Schedule', default=False)
    nuevo_activo = BooleanField('¿Es un nuevo activo?', default=False)
    responsable = StringField('Responsable', validators=[Optional()])
    emails = StringField('Correos del Responsable (separados por comas)', validators=[Optional()])
    tipo = SelectField(
        'Tipo de Activo',
        choices=[
            ('aplicacion_web', 'Aplicación Web'),
            ('blog_portal_web', 'Blog/Portal Web'),
            ('servicio_web', 'Servicio Web'),
            ('app', 'App'),
            ('app_web', 'App Web')
        ],
        validators=[Optional()], default=None
    )
    periodicidad = SelectField(
        'Periodicidad de Auditoría',
        choices=[
            ('1', '1 Mes'),
            ('3', '3 Meses'),
            ('6', '6 Meses'),
            ('12', '12 Meses')
        ],
        validators=[Optional()], default=None
    )
    
    scanDateTime = DateTimeLocalField("Select Date & Time", format='%Y-%m-%dT%H:%M', validators=[Optional()], render_kw={"class": "form-control"})
    submit = SubmitField('Start Scan')

    def validate_scanDateTime(self, field):
        if self.schedule.data and not field.data:
            raise ValidationError('Data and Time is required if you are scheduling the scan')