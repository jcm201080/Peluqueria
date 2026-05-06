from flask import Blueprint, render_template, redirect, url_for, request, flash
from database.models import db, Usuario
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        
        # Evitar duplicados al registrar
        usuario_existente = Usuario.query.filter_by(telefono=telefono).first()
        if usuario_existente:
            # Podemos añadir categorías a los mensajes flash para estilizarlos en CSS (ej: 'error' o 'success')
            flash('Este número de teléfono ya está registrado. Intenta iniciar sesión.', 'error')
            return redirect(url_for('auth.registro'))
        
        # Hasheo de contraseña y creación del usuario
        pw_hash = generate_password_hash(password).decode('utf8')
        nuevo_usuario = Usuario(nombre=nombre, telefono=telefono, password=pw_hash)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # --- MEJORA: Iniciar sesión automáticamente ---
        # Como acabamos de hacer commit, 'nuevo_usuario' ya es un objeto válido de la DB
        login_user(nuevo_usuario)
        
        flash('Registro completado. ¡Bienvenido/a! Ya puedes reservar tu cita.', 'success')
        
        # Redirigimos directamente a la página de contacto/reservas
        return redirect(url_for('cita.contacto'))
        
    return render_template('registro.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        user = Usuario.query.filter_by(telefono=telefono).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Ya que mejoramos la UX, si el usuario hace login, también le podemos mandar a contacto 
            # para que reserve directamente, o dejarlo en el index si lo prefieres.
            return redirect(url_for('citas.contacto')) 
        else:
            flash('Teléfono o contraseña incorrectos.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # Añadimos esta buena práctica: solo un usuario logueado puede desloguearse
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        nueva_pass = request.form.get('password')
        
        user = Usuario.query.filter_by(telefono=telefono).first()
        if user:
            # Encriptamos la nueva clave
            user.password = generate_password_hash(nueva_pass).decode('utf8')
            db.session.commit()
            flash('Contraseña actualizada con éxito. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No encontramos ningún usuario con ese teléfono.', 'error')
            
    return render_template('recuperar.html')