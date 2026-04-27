from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .. import db
from ..models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html',
        total_created=current_user.created_tasks.count(),
        total_assigned=current_user.assigned_tasks.count(),
        completed=current_user.assigned_tasks.filter_by(status='completed').count(),
        pending=current_user.assigned_tasks.filter_by(status='pending').count())

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        if not full_name:
            flash('El nombre completo es requerido.', 'danger')
            return render_template('users/edit_profile.html')
        if not email or '@' not in email:
            flash('Ingresa un correo electrónico válido.', 'danger')
            return render_template('users/edit_profile.html')
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            flash('Ese correo ya está registrado por otro usuario.', 'danger')
            return render_template('users/edit_profile.html')
        current_user.full_name = full_name
        current_user.email = email
        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('users.profile'))
    return render_template('users/edit_profile.html')

@users_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('users/change_password.html')
        if len(new_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('users/change_password.html')
        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden.', 'danger')
            return render_template('users/change_password.html')
        current_user.set_password(new_password)
        db.session.commit()
        flash('Contraseña cambiada exitosamente.', 'success')
        return redirect(url_for('users.profile'))
    return render_template('users/change_password.html')

@users_bp.route('/list')
@login_required
def list_users():
    if current_user.role != 'admin':
        abort(403)
    return render_template('users/list.html', users=User.query.all())
