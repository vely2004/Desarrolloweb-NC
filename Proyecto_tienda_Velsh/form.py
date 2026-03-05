from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class PedidoForm(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[DataRequired()]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    celular = StringField(
        "Celular",
        validators=[DataRequired()]
    )

    direccion = StringField(
        "Dirección",
        validators=[DataRequired()]
    )

    producto = TextAreaField(
        "Producto",
        validators=[DataRequired()]
    )

    submit = SubmitField("Enviar pedido")