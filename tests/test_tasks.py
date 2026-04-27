import pytest
from app import db
from app.models import Task, User

class TestCrearTarea:
    def test_CP_T_01_crear_tarea_valida(self, logged_client, sample_user, app):
        r = logged_client.post('/tasks/create', data={'title':'Tarea nueva','priority':'medium'}, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            assert Task.query.filter_by(title='Tarea nueva').first() is not None

    def test_CP_T_02_sin_titulo_falla(self, logged_client, app):
        r = logged_client.post('/tasks/create', data={'title':'','priority':'medium'}, follow_redirects=True)
        assert b'obligatorio' in r.data

    def test_CP_T_03_titulo_muy_largo(self, logged_client, app):
        r = logged_client.post('/tasks/create', data={'title':'A'*201,'priority':'medium'}, follow_redirects=True)
        assert b'200' in r.data or b'superar' in r.data

class TestEditarEliminar:
    def test_CP_T_04_editar_tarea(self, logged_client, sample_task, app):
        with app.app_context():
            task = Task.query.filter_by(title='Tarea de prueba').first()
            r = logged_client.post(f'/tasks/{task.id}/edit',
                data={'title':'Actualizada','priority':'high','status':'in_progress'}, follow_redirects=True)
            assert r.status_code == 200

    def test_CP_T_05_eliminar_tarea(self, logged_client, sample_task, app):
        with app.app_context():
            task = Task.query.filter_by(title='Tarea de prueba').first()
            task_id = task.id
        r = logged_client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            assert Task.query.get(task_id) is None

    def test_CP_T_06_editar_ajena_403(self, client, sample_user, second_user, app):
        with app.app_context():
            user2 = User.query.filter_by(username='user2').first()
            task = Task(title='Ajena', creator_id=user2.id, priority='low')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        client.post('/auth/login', data={'username':'testuser','password':'password123'})
        r = client.post(f'/tasks/{task_id}/edit', data={'title':'x','priority':'low','status':'pending'}, follow_redirects=True)
        assert r.status_code == 403

class TestFiltros:
    def test_CP_T_07_filtrar_completadas(self, logged_client, sample_user, app):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            t = Task(title='Completada',priority='low',status='completed',creator_id=user.id)
            db.session.add(t)
            db.session.commit()
        r = logged_client.get('/tasks/?status=completed')
        assert b'Completada' in r.data

    def test_CP_T_08_busqueda_texto(self, logged_client, sample_user, app):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            t = Task(title='Revisar maquinaria',priority='high',creator_id=user.id)
            db.session.add(t)
            db.session.commit()
        r = logged_client.get('/tasks/?q=maquinaria')
        assert b'maquinaria' in r.data.lower()
