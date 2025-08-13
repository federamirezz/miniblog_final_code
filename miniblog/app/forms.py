from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    nombre_usuario = StringField('Nombre de usuario', validators=[DataRequired()])
    correo = StringField('Correo electrónico', validators=[Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    nombre_usuario = StringField('Nombre de usuario', validators=[DataRequired()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

class PostForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    categoria = SelectField('Categoría', coerce=int)
    submit = SubmitField('Publicar')

class ComentarioForm(FlaskForm):
    texto = TextAreaField('Comentario', validators=[DataRequired()])
    submit = SubmitField('Comentar')
