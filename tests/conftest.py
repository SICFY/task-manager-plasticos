import pytest
from app import create_app, db
from app.models import User, Task

@pytest.fixture(scope='function')
def app():
    application = create_app('testing')
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@test.com', full_name='Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User(username='admintest', email='admin@test.com', full_name='Admin User', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def second_user(app):
    with app.app_context():
        user = User(username='user2', email='user2@test.com', full_name='Second User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def logged_client(client, sample_user, app):
    with app.app_context():
        client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client, admin_user, app):
    with app.app_context():
        client.post('/auth/login', data={'username': 'admintest', 'password': 'admin123'}, follow_redirects=True)
    return client

@pytest.fixture
def sample_task(app, sample_user):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        task = Task(title='Tarea de prueba', description='Descripcion', priority='medium', creator_id=user.id)
        db.session.add(task)
        db.session.commit()
        return task
