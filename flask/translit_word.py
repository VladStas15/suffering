from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class TranslitForm(FlaskForm):
    vvod = StringField("Введите текст на русском: ", validators=[DataRequired()])
    submit = SubmitField("Перевести")