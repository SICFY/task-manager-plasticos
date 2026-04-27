from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.list_tasks'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        errors = []
        if not username or len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if not email or '@' not in email:
            errors.append('Ingresa un correo electrónico válido.')
        if not full_name:
            errors.append('El nombre completo es requerido.')
        if not password or len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden.')
        if User.query.filter_by(username=username).first():
            errors.append('El nombre de usuario ya está en uso.')
        if User.query.filter_by(email=email).first():
            errors.append('El correo electrónico ya está registrado.')
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.list_tasks'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña.', 'danger')
            return render_template('auth/login.html')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            flash(f'¡Bienvenido, {user.full_name}!', 'success')
            return redirect(next_page or url_for('tasks.list_tasks'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('auth.login'))
