import os
from app import create_app, db
from app.models import User, Task

app = create_app(os.environ.get('FLASK_ENV', 'default'))

@app.cli.command('seed-db')
def seed_db():
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@plasticos.com', full_name='Administrador', role='admin')
        admin.set_password('admin123')
        emp1 = User(username='jperez', email='jperez@plasticos.com', full_name='Juan Perez')
        emp1.set_password('emp123')
        db.session.add_all([admin, emp1])
        db.session.commit()
        from datetime import datetime, timedelta
        t = Task(title='Revisar maquinaria', priority='high', creator_id=admin.id,
                 assignee_id=emp1.id, due_date=datetime.utcnow()+timedelta(days=3))
        db.session.add(t)
        db.session.commit()
        print('Base de datos lista. Admin: admin/admin123')

if __name__ == '__main__':
    app.run(debug=True)
