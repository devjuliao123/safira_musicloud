from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    if not User.query.filter_by(username='adm').first():
        user = User(username='adm')
        user.set_password('adm')
        db.session.add(user)
        db.session.commit()
        print("User adm created successfully.")
    else:
        print("User adm already exists.")
