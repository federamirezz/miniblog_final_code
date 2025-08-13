from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField("Repetir contraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Crear cuenta")

class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")

class PostForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=100)])
    contenido = TextAreaField("Contenido", validators=[DataRequired(), Length(min=1)])
    categoria = SelectField("Categoría", coerce=int)
    submit = SubmitField("Publicar")

class CommentForm(FlaskForm):
    texto = TextAreaField("Comentario", validators=[DataRequired(), Length(min=1)])
    submit = SubmitField("Comentar")
