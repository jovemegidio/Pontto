from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ponto.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_senha(senha):
            if not usuario.ativo:
                flash('Sua conta está desativada. Contate o administrador.', 'danger')
                return render_template('login.html')
            login_user(usuario, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('ponto.dashboard'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')

        if nome:
            current_user.nome = nome

        if nova_senha:
            if not current_user.check_senha(senha_atual):
                flash('Senha atual incorreta.', 'danger')
                return render_template('perfil.html')
            if nova_senha != confirmar_senha:
                flash('As senhas não conferem.', 'danger')
                return render_template('perfil.html')
            if len(nova_senha) < 6:
                flash('A nova senha deve ter no mínimo 6 caracteres.', 'danger')
                return render_template('perfil.html')
            current_user.set_senha(nova_senha)

        db.session.commit()
        flash('Perfil atualizado com sucesso.', 'success')

    return render_template('perfil.html')
