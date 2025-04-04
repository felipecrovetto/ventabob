from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from .forms import LoginForm, RegistrationForm  # Asegúrate de crear RegistrationForm
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()  # Necesitas crear este formulario en forms.py
    if form.validate_on_submit():
        # Aquí va la lógica para crear un nuevo usuario
        # Ejemplo:
        # username = form.username.data
        # email = form.email.data
        # password = form.password.data
        # new_user = User(username=username, email=email, password=password, role='customer') # O el rol por defecto
        # db.session.add(new_user)
        # db.session.commit()
        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registrarse', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))