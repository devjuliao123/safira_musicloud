from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import check_password_hash
from app.database import get_db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/entrar', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')
        
        with get_db() as conn:
            user = conn.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,)).fetchone()

        if user and check_password_hash(user['senha_hash'], senha):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['usuario']
            return redirect(url_for('main.menu'))
        else:
            flash('Login inválido. Tente novamente.')
            
    return render_template('login.html')

@auth_bp.route('/sair')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
