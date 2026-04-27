import pytest
from app import db
from app.models import User

class TestRegistro:
    def test_CP_A_01_registro_exitoso(self, client, app):
        r = client.post('/auth/register', data={'username':'newuser','email':'new@test.com',
            'full_name':'New','password':'pass123','confirm_password':'pass123'}, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            assert User.query.filter_by(username='newuser').first() is not None

    def test_CP_A_02_username_duplicado(self, client, sample_user, app):
        r = client.post('/auth/register', data={'username':'testuser','email':'otro@test.com',
            'full_name':'Otro','password':'pass123','confirm_password':'pass123'}, follow_redirects=True)
        assert b'uso' in r.data or b'est' in r.data

    def test_CP_A_03_passwords_no_coinciden(self, client, app):
        r = client.post('/auth/register', data={'username':'fail','email':'fail@test.com',
            'full_name':'Fail','password':'pass123','confirm_password':'diferente'}, follow_redirects=True)
        assert b'coinciden' in r.data

    def test_CP_A_04_password_muy_corta(self, client, app):
        r = client.post('/auth/register', data={'username':'short','email':'short@test.com',
            'full_name':'Short','password':'123','confirm_password':'123'}, follow_redirects=True)
        assert b'6' in r.data or b'caracteres' in r.data

class TestLogin:
    def test_CP_L_01_login_exitoso(self, client, sample_user, app):
        r = client.post('/auth/login', data={'username':'testuser','password':'password123'}, follow_redirects=True)
        assert b'Bienvenido' in r.data

    def test_CP_L_02_login_incorrecto(self, client, sample_user, app):
        r = client.post('/auth/login', data={'username':'testuser','password':'wrong'}, follow_redirects=True)
        assert b'incorrectos' in r.data

    def test_CP_L_03_sin_sesion_redirige(self, client, app):
        r = client.get('/tasks/', follow_redirects=False)
        assert r.status_code == 302

    def test_CP_L_04_logout(self, logged_client, app):
        r = logged_client.get('/auth/logout', follow_redirects=True)
        assert b'cerrada' in r.data
