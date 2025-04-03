from flask import Blueprint, render_template
from flask_login import login_required
from . import app

# No estamos creando un Blueprint aquí, sino usando la instancia 'app' directamente

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Aquí puedes definir otras rutas directamente asociadas a la aplicación
# Ejemplo:
# @app.route('/otra_ruta')
# @login_required
# def otra_vista():
#     return render_template('otra_pagina.html')