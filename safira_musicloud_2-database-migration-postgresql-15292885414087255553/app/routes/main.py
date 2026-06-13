from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from .auth import login_required
from app.database import get_db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.menu'))
    return redirect(url_for('auth.login'))

@main_bp.route('/menu')
@login_required
def menu():
    dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    hoje_idx = datetime.now().weekday()
    hoje_str = dias[hoje_idx]

    with get_db() as conn:
        # Busca a agenda dos professores para o dia de hoje
        agendas = conn.execute('''
            SELECT a.*, p.nome as nome_professor
            FROM agendas a
            JOIN pessoas p ON a.professor_id = p.id
            WHERE a.dia_semana = %s
            ORDER BY a.hora_inicio
        ''', (hoje_str,)).fetchall()

    return render_template('menu.html', schedules=agendas, today=hoje_str.capitalize())

@main_bp.route('/pessoas')
@login_required
def people():
    with get_db() as conn:
        lista_pessoas = conn.execute('SELECT * FROM pessoas ORDER BY nome').fetchall()
    return render_template('people.html', people=lista_pessoas)

@main_bp.route('/pessoas/adicionar', methods=['POST'])
@login_required
def add_person():
    nome = (request.form.get('name') or '').upper()
    tipo = request.form.get('type') # 'student' ou 'teacher' do form -> mapear
    if tipo == 'student': tipo = 'aluno'
    elif tipo == 'teacher': tipo = 'professor'

    email = (request.form.get('email') or '').upper()
    telefone = request.form.get('phone')
    data_nascimento = request.form.get('birth_date')
    possui_responsavel = 1 if request.form.get('has_guardian') else 0
    nome_responsavel = (request.form.get('guardian_name') or '').upper()
    telefone_responsavel = request.form.get('guardian_phone')
    cpf = request.form.get('cpf')
    cpf_responsavel = request.form.get('guardian_cpf')
    
    if nome and tipo:
        with get_db() as conn:
            # Verificar duplicidade de nome
            existente = conn.execute('SELECT id FROM pessoas WHERE UPPER(nome) = %s', (nome,)).fetchone()
            if existente:
                flash('NÃO FOI POSSÍVEL CADASTRAR: JÁ EXISTE UMA PESSOA COM ESTE NOME NO SISTEMA!', 'error')
                return redirect(url_for('main.people'))

            # Verificar duplicidade de CPF para o mesmo tipo comercial
            if cpf:
                cpf_existente = conn.execute('SELECT id FROM pessoas WHERE cpf = %s AND tipo = %s', (cpf, tipo)).fetchone()
                if cpf_existente:
                    rel = 'ALUNO' if tipo == 'aluno' else 'PROFESSOR'
                    flash(f'NÃO FOI POSSÍVEL CADASTRAR: ESTE CPF JÁ ESTÁ REGISTRADO PARA OUTRO {rel}!', 'error')
                    return redirect(url_for('main.people'))

            conn.execute('''
                INSERT INTO pessoas (nome, tipo, email, telefone, data_nascimento, possui_responsavel, nome_responsavel, telefone_responsavel, ativo, cpf, cpf_responsavel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s)
            ''', (nome, tipo, email, telefone, data_nascimento, possui_responsavel, nome_responsavel, telefone_responsavel, cpf, cpf_responsavel))
            conn.commit()
            flash('PESSOA CADASTRADA COM SUCESSO!', 'success')
    
    return redirect(url_for('main.people'))

@main_bp.route('/pessoas/editar/<int:id>', methods=['POST'])
@login_required
def edit_person(id):
    nome = (request.form.get('name') or '').upper()
    tipo = request.form.get('type')
    if tipo == 'student': tipo = 'aluno'
    elif tipo == 'teacher': tipo = 'professor'

    email = (request.form.get('email') or '').upper()
    telefone = request.form.get('phone')
    data_nascimento = request.form.get('birth_date')
    possui_responsavel = 1 if request.form.get('has_guardian') else 0
    nome_responsavel = (request.form.get('guardian_name') or '').upper()
    telefone_responsavel = request.form.get('guardian_phone')
    ativo = 1 if request.form.get('active') else 0
    cpf = request.form.get('cpf')
    cpf_responsavel = request.form.get('guardian_cpf')
    
    if nome and tipo:
        with get_db() as conn:
            # Verificar se mudou o nome para um que já existe
            existente = conn.execute('SELECT id FROM pessoas WHERE UPPER(nome) = %s AND id != %s', (nome, id)).fetchone()
            if existente:
                flash('NÃO FOI POSSÍVEL ATUALIZAR: JÁ EXISTE OUTRA PESSOA COM ESTE NOME NO SISTEMA!', 'error')
                return redirect(url_for('main.people'))

            # Verificar duplicidade de CPF para o mesmo tipo comercial
            if cpf:
                cpf_existente = conn.execute('SELECT id FROM pessoas WHERE cpf = %s AND tipo = %s AND id != %s', (cpf, tipo, id)).fetchone()
                if cpf_existente:
                    rel = 'ALUNO' if tipo == 'aluno' else 'PROFESSOR'
                    flash(f'NÃO FOI POSSÍVEL ATUALIZAR: ESTE CPF JÁ ESTÁ REGISTRADO PARA OUTRO {rel}!', 'error')
                    return redirect(url_for('main.people'))

            conn.execute('''
                UPDATE pessoas
                SET nome = %s, tipo = %s, email = %s, telefone = %s, data_nascimento = %s, possui_responsavel = %s, nome_responsavel = %s, telefone_responsavel = %s, ativo = %s, cpf = %s, cpf_responsavel = %s
                WHERE id = %s
            ''', (nome, tipo, email, telefone, data_nascimento, possui_responsavel, nome_responsavel, telefone_responsavel, ativo, cpf, cpf_responsavel, id))
            conn.commit()
            flash('CADASTRO ATUALIZADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.people'))

@main_bp.route('/pessoas/deletar/<int:id>')
@login_required
def delete_person(id):
    with get_db() as conn:
        # Verificar vínculos
        tem_curso = conn.execute('SELECT id FROM cursos WHERE professor_id = %s', (id,)).fetchone()
        tem_agenda = conn.execute('SELECT id FROM agendas WHERE professor_id = %s', (id,)).fetchone()
        tem_presenca = conn.execute('SELECT id FROM presencas WHERE aluno_id = %s', (id,)).fetchone()

        if tem_curso or tem_agenda or tem_presenca:
            conn.execute('UPDATE pessoas SET ativo = 0 WHERE id = %s', (id,))
            conn.commit()
            flash('ESTE CADASTRO POSSUI VÍNCULOS E NÃO PODE SER EXCLUÍDO. ELE FOI DESATIVADO AUTOMATICAMENTE.', 'info')
            return redirect(url_for('main.people'))

        conn.execute('DELETE FROM pessoas WHERE id = %s', (id,))
        conn.commit()
    flash('CADASTRO EXCLUÍDO COM SUCESSO!', 'success')
    return redirect(url_for('main.people'))

@main_bp.route('/cursos')
@login_required
def courses():
    with get_db() as conn:
        lista_cursos = conn.execute('''
            SELECT c.*, p.nome as nome_professor
            FROM cursos c
            LEFT JOIN pessoas p ON c.professor_id = p.id
            ORDER BY c.nome
        ''').fetchall()
        professores = conn.execute("SELECT * FROM pessoas WHERE tipo = 'professor' AND ativo = 1 ORDER BY nome").fetchall()
    return render_template('courses.html', courses=lista_cursos, teachers=professores)

@main_bp.route('/cursos/adicionar', methods=['POST'])
@login_required
def add_course():
    nome = (request.form.get('name') or '').upper()
    carga_horaria = request.form.get('workload')
    professor_id = request.form.get('teacher_id')
    
    if nome:
        with get_db() as conn:
            conn.execute('INSERT INTO cursos (nome, carga_horaria, professor_id) VALUES (%s, %s, %s)',
                       (nome, carga_horaria, professor_id or None))
            conn.commit()
            flash('CURSO CADASTRADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.courses'))

@main_bp.route('/cursos/editar/<int:id>', methods=['POST'])
@login_required
def edit_course(id):
    nome = (request.form.get('name') or '').upper()
    carga_horaria = request.form.get('workload')
    professor_id = request.form.get('teacher_id')
    
    if nome:
        with get_db() as conn:
            conn.execute('UPDATE cursos SET nome = %s, carga_horaria = %s, professor_id = %s WHERE id = %s',
                       (nome, carga_horaria, professor_id or None, id))
            conn.commit()
            flash('CURSO ATUALIZADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.courses'))

@main_bp.route('/cursos/deletar/<int:id>')
@login_required
def delete_course(id):
    with get_db() as conn:
        conn.execute('DELETE FROM cursos WHERE id = %s', (id,))
        conn.commit()
    flash('CURSO EXCLUÍDO COM SUCESSO!', 'success')
    return redirect(url_for('main.courses'))

@main_bp.route('/agenda')
@login_required
def schedule():
    with get_db() as conn:
        lista_agendas = conn.execute('''
            SELECT a.*, p.nome as nome_professor
            FROM agendas a
            JOIN pessoas p ON a.professor_id = p.id
            ORDER BY CASE a.dia_semana
                WHEN 'segunda-feira' THEN 1
                WHEN 'terça-feira' THEN 2
                WHEN 'quarta-feira' THEN 3
                WHEN 'quinta-feira' THEN 4
                WHEN 'sexta-feira' THEN 5
                WHEN 'sábado' THEN 6
                WHEN 'domingo' THEN 7
            END, a.hora_inicio
        ''').fetchall()
        professores = conn.execute("SELECT * FROM pessoas WHERE tipo = 'professor' AND ativo = 1 ORDER BY nome").fetchall()
    return render_template('schedule.html', schedules=lista_agendas, teachers=professores)

@main_bp.route('/agenda/adicionar', methods=['POST'])
@login_required
def add_schedule():
    professor_id = request.form.get('teacher_id')
    dia_semana = request.form.get('day_of_week')
    hora_inicio = request.form.get('start_time')
    hora_fim = request.form.get('end_time')
    nome_curso = (request.form.get('course_name') or '').upper()
    sala = (request.form.get('room') or '').upper()
    
    if professor_id and dia_semana and hora_inicio and hora_fim:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO agendas (professor_id, dia_semana, hora_inicio, hora_fim, nome_curso, sala)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (professor_id, dia_semana, hora_inicio, hora_fim, nome_curso, sala))
            conn.commit()
            flash('HORÁRIO ADICIONADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.schedule'))

@main_bp.route('/agenda/editar/<int:id>', methods=['POST'])
@login_required
def edit_schedule(id):
    professor_id = request.form.get('teacher_id')
    dia_semana = request.form.get('day_of_week')
    hora_inicio = request.form.get('start_time')
    hora_fim = request.form.get('end_time')
    nome_curso = (request.form.get('course_name') or '').upper()
    sala = (request.form.get('room') or '').upper()
    
    if professor_id and dia_semana and hora_inicio and hora_fim:
        with get_db() as conn:
            conn.execute('''
                UPDATE agendas
                SET professor_id = %s, dia_semana = %s, hora_inicio = %s, hora_fim = %s, nome_curso = %s, sala = %s
                WHERE id = %s
            ''', (professor_id, dia_semana, hora_inicio, hora_fim, nome_curso, sala, id))
            conn.commit()
            flash('HORÁRIO ATUALIZADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.schedule'))

@main_bp.route('/agenda/deletar/<int:id>')
@login_required
def delete_schedule(id):
    with get_db() as conn:
        conn.execute('DELETE FROM agendas WHERE id = %s', (id,))
        conn.commit()
    flash('HORÁRIO EXCLUÍDO COM SUCESSO!', 'success')
    return redirect(url_for('main.schedule'))

@main_bp.route('/presenca')
@login_required
def attendance():
    with get_db() as conn:
        # Pega todas as presenças registradas
        lista_presencas = conn.execute('''
            SELECT pr.*, p.nome as nome_aluno, a.nome_curso, t.nome as nome_professor
            FROM presencas pr
            JOIN pessoas p ON pr.aluno_id = p.id
            JOIN agendas a ON pr.agenda_id = a.id
            JOIN pessoas t ON a.professor_id = t.id
            ORDER BY pr.data DESC
        ''').fetchall()

        # Dados para o formulário de adição
        alunos = conn.execute("SELECT * FROM pessoas WHERE tipo = 'aluno' AND ativo = 1 ORDER BY nome").fetchall()
        agendas = conn.execute('''
            SELECT a.*, p.nome as nome_professor
            FROM agendas a
            JOIN pessoas p ON a.professor_id = p.id
        ''').fetchall()
    
    return render_template('attendance.html', attendances=lista_presencas, students=alunos, schedules=agendas)

@main_bp.route('/presenca/adicionar', methods=['POST'])
@login_required
def add_attendance():
    agenda_id = request.form.get('schedule_id')
    aluno_id = request.form.get('student_id')
    data = request.form.get('date')
    status = request.form.get('status')
    
    if agenda_id and aluno_id and data and status:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO presencas (agenda_id, aluno_id, data, status)
                VALUES (%s, %s, %s, %s)
            ''', (agenda_id, aluno_id, data, status))
            conn.commit()
            flash('ASSINATURA REGISTRADA COM SUCESSO!', 'success')
    
    return redirect(url_for('main.attendance'))

@main_bp.route('/presenca/deletar/<int:id>')
@login_required
def delete_attendance(id):
    with get_db() as conn:
        conn.execute('DELETE FROM presencas WHERE id = %s', (id,))
        conn.commit()
    flash('ASSINATURA EXCLUÍDA COM SUCESSO!', 'success')
    return redirect(url_for('main.attendance'))

@main_bp.route('/financeiro')
@login_required
def finance():
    with get_db() as conn:
        transacoes = conn.execute('SELECT * FROM financeiro ORDER BY data DESC').fetchall()

        # Cálculos simples
        total_receita = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'receita'").fetchone()['sum'] or 0
        total_despesa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'despesa'").fetchone()['sum'] or 0
        saldo = total_receita - total_despesa
    
    return render_template('finance.html', 
                           transactions=transacoes,
                           total_receita=total_receita, 
                           total_despesa=total_despesa, 
                           saldo=saldo)

@main_bp.route('/financeiro/adicionar', methods=['POST'])
@login_required
def add_transaction():
    descricao = (request.form.get('description') or '').upper()
    valor = request.form.get('amount')
    tipo = request.form.get('type')
    data = request.form.get('date')
    status = (request.form.get('status') or '').upper()
    
    if descricao and valor and tipo and data:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO financeiro (descricao, valor, tipo, data, status)
                VALUES (%s, %s, %s, %s, %s)
            ''', (descricao, valor, tipo, data, status))
            conn.commit()
            flash('LANÇAMENTO FINANCEIRO REALIZADO COM SUCESSO!', 'success')
    
    return redirect(url_for('main.finance'))

@main_bp.route('/financeiro/deletar/<int:id>')
@login_required
def delete_transaction(id):
    with get_db() as conn:
        conn.execute('DELETE FROM financeiro WHERE id = %s', (id,))
        conn.commit()
    flash('LANÇAMENTO FINANCEIRO EXCLUÍDO COM SUCESSO!', 'success')
    return redirect(url_for('main.finance'))
