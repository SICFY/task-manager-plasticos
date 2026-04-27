import pytest
from app import db
from app.models import User, Task

class TestFlujoCompleto:
    def test_CP_INT_01_registro_login_crear_completar(self, client, app):
        client.post('/auth/register', data={'username':'intuser','email':'int@test.com',
            'full_name':'Int User','password':'pass1234','confirm_password':'pass1234'}, follow_redirects=True)
        r = client.post('/auth/login', data={'username':'intuser','password':'pass1234'}, follow_redirects=True)
        assert b'Bienvenido' in r.data
        client.post('/tasks/create', data={'title':'Tarea integral','priority':'high'}, follow_redirects=True)
        with app.app_context():
            task = Task.query.filter_by(title='Tarea integral').first()
            assert task is not None
            task_id = task.id
        r2 = client.post(f'/tasks/{task_id}/complete', follow_redirects=True)
        assert r2.status_code == 200
        with app.app_context():
            assert Task.query.get(task_id).status == Task.STATUS_COMPLETED

    def test_CP_INT_02_admin_ve_lista_usuarios(self, admin_client, app):
        r = admin_client.get('/users/list')
        assert r.status_code == 200

    def test_CP_INT_03_empleado_no_ve_usuarios(self, logged_client, app):
        r = logged_client.get('/users/list')
        assert r.status_code == 403
