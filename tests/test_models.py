import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, Task

class TestUserModel:
    def test_CP_U_01_crear_usuario_valido(self, app):
        with app.app_context():
            user = User(username='nuevo', email='nuevo@test.com', full_name='Nuevo')
            user.set_password('secure123')
            db.session.add(user)
            db.session.commit()
            assert User.query.filter_by(username='nuevo').first() is not None

    def test_CP_U_02_password_hasheada(self, app):
        with app.app_context():
            user = User(username='hash', email='hash@test.com', full_name='Hash')
            user.set_password('miClave')
            assert user.password_hash != 'miClave'

    def test_CP_U_03_check_password_correcta(self, app):
        with app.app_context():
            user = User(username='pw', email='pw@test.com', full_name='PW')
            user.set_password('correcta123')
            assert user.check_password('correcta123') is True

    def test_CP_U_04_check_password_incorrecta(self, app):
        with app.app_context():
            user = User(username='pw2', email='pw2@test.com', full_name='PW2')
            user.set_password('correcta123')
            assert user.check_password('incorrecta') is False

    def test_CP_U_05_username_unico(self, app, sample_user):
        with app.app_context():
            from sqlalchemy.exc import IntegrityError
            dup = User(username='testuser', email='otro@test.com', full_name='Dup')
            dup.set_password('pass')
            db.session.add(dup)
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_CP_U_06_to_dict_sin_password(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            d = user.to_dict()
            assert 'password_hash' not in d

class TestTaskModel:
    def test_CP_U_07_estado_default_pending(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title='Test', creator_id=user.id)
            db.session.add(task)
            db.session.commit()
            assert task.status == Task.STATUS_PENDING

    def test_CP_U_08_prioridad_default_medium(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title='Test', creator_id=user.id)
            db.session.add(task)
            db.session.commit()
            assert task.priority == Task.PRIORITY_MEDIUM

    def test_CP_U_09_is_completed_true(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title='Done', creator_id=user.id, status=Task.STATUS_COMPLETED)
            db.session.add(task)
            db.session.commit()
            assert task.is_completed() is True

    def test_CP_U_10_is_overdue_vencida(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title='Vencida', creator_id=user.id, due_date=datetime.utcnow()-timedelta(days=1))
            db.session.add(task)
            db.session.commit()
            assert task.is_overdue() is True

    def test_CP_U_11_is_overdue_futura(self, app, sample_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title='Futura', creator_id=user.id, due_date=datetime.utcnow()+timedelta(days=5))
            db.session.add(task)
            db.session.commit()
            assert task.is_overdue() is False
