from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class AddProductForm(FlaskForm):
    code = StringField('Código del Producto', validators=[DataRequired()])
    name = StringField('Nombre del Producto', validators=[DataRequired()])
    price = FloatField('Precio de Venta', validators=[DataRequired(), NumberRange(min=0)])
    cost = FloatField('Costo del Producto', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock Inicial', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Agregar Producto')

class SellProductForm(FlaskForm):
    product_code = StringField('Código del Producto', validators=[DataRequired()])
    quantity = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    payment_method = SelectField('Método de Pago', choices=[('cash', 'Efectivo'), ('card', 'Tarjeta')], validators=[DataRequired()])
    submit = SubmitField('Vender')

class AddStockForm(FlaskForm):
    existing_product_code = StringField('Buscar Producto por Código', validators=[DataRequired()])
    submit = SubmitField('Buscar')

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Registrarse')