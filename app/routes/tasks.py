from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from .. import db
from ..models import Task, User

tasks_bp = Blueprint('tasks', __name__)

def parse_due_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    return None

@tasks_bp.route('/')
@login_required
def list_tasks():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    search_query = request.args.get('q', '').strip()
    query = Task.query
    if current_user.role != 'admin':
        query = query.filter((Task.creator_id == current_user.id) | (Task.assignee_id == current_user.id))
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    if search_query:
        query = query.filter(Task.title.ilike(f'%{search_query}%') | Task.description.ilike(f'%{search_query}%'))
    tasks = query.order_by(Task.created_at.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    pending = [t for t in tasks if t.status == Task.STATUS_PENDING]
    in_progress = [t for t in tasks if t.status == Task.STATUS_IN_PROGRESS]
    completed = [t for t in tasks if t.status == Task.STATUS_COMPLETED]
    return render_template('tasks/list.html', tasks=tasks, pending=pending,
        in_progress=in_progress, completed=completed, users=users,
        status_filter=status_filter, priority_filter=priority_filter, search_query=search_query)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', Task.PRIORITY_MEDIUM)
        assignee_id = request.form.get('assignee_id')
        due_date_str = request.form.get('due_date', '')
        if not title:
            flash('El título es obligatorio.', 'danger')
            return render_template('tasks/form.html', users=User.query.filter_by(is_active=True).all())
        if len(title) > 200:
            flash('El título no puede superar los 200 caracteres.', 'danger')
            return render_template('tasks/form.html', users=User.query.filter_by(is_active=True).all())
        task = Task(title=title, description=description, priority=priority,
            creator_id=current_user.id,
            assignee_id=int(assignee_id) if assignee_id else None,
            due_date=parse_due_date(due_date_str))
        db.session.add(task)
        db.session.commit()
        flash('Tarea creada exitosamente.', 'success')
        return redirect(url_for('tasks.list_tasks'))
    return render_template('tasks/form.html', users=User.query.filter_by(is_active=True).all(), task=None)

@tasks_bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin':
        if task.creator_id != current_user.id and task.assignee_id != current_user.id:
            abort(403)
    return render_template('tasks/detail.html', task=task)

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin' and task.creator_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('El título es obligatorio.', 'danger')
            return render_template('tasks/form.html', task=task, users=User.query.filter_by(is_active=True).all())
        task.title = title
        task.description = request.form.get('description', '').strip()
        task.status = request.form.get('status', Task.STATUS_PENDING)
        task.priority = request.form.get('priority', Task.PRIORITY_MEDIUM)
        assignee_id = request.form.get('assignee_id')
        task.assignee_id = int(assignee_id) if assignee_id else None
        task.due_date = parse_due_date(request.form.get('due_date', ''))
        task.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Tarea actualizada exitosamente.', 'success')
        return redirect(url_for('tasks.view_task', task_id=task.id))
    return render_template('tasks/form.html', task=task, users=User.query.filter_by(is_active=True).all())

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin' and task.creator_id != current_user.id:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada exitosamente.', 'success')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin':
        if task.creator_id != current_user.id and task.assignee_id != current_user.id:
            abort(403)
    task.status = Task.STATUS_COMPLETED
    task.updated_at = datetime.utcnow()
    db.session.commit()
    flash('¡Tarea marcada como completada!', 'success')
    return redirect(url_for('tasks.list_tasks'))
