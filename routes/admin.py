from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, timedelta, datetime
from extensions import db
from models import Usuario, RegistroPonto

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('ponto.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def painel():
    hoje = date.today()
    total_funcionarios = Usuario.query.filter_by(ativo=True).count()
    registros_hoje = RegistroPonto.query.filter_by(data=hoje).count()
    usuarios_hoje = db.session.query(RegistroPonto.usuario_id).filter_by(
        data=hoje
    ).distinct().count()

    ultimos_registros = RegistroPonto.query.filter_by(data=hoje).order_by(
        RegistroPonto.data_hora.desc()
    ).limit(20).all()

    return render_template('admin/painel.html',
                           total_funcionarios=total_funcionarios,
                           registros_hoje=registros_hoje,
                           usuarios_hoje=usuarios_hoje,
                           ultimos_registros=ultimos_registros,
                           hoje=hoje,
                           label_tipo=RegistroPonto.label_tipo)


@admin_bp.route('/funcionarios')
@login_required
@admin_required
def funcionarios():
    usuarios = Usuario.query.order_by(Usuario.nome.asc()).all()
    return render_template('admin/funcionarios.html', usuarios=usuarios)


@admin_bp.route('/funcionario/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_funcionario():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        cargo = request.form.get('cargo', '').strip()
        departamento = request.form.get('departamento', '').strip()
        is_admin = request.form.get('is_admin') == 'on'

        if not nome or not email or not senha:
            flash('Nome, e-mail e senha são obrigatórios.', 'danger')
            return render_template('admin/form_funcionario.html', usuario=None)

        if len(senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
            return render_template('admin/form_funcionario.html', usuario=None)

        if Usuario.query.filter_by(email=email).first():
            flash('Já existe um usuário com este e-mail.', 'danger')
            return render_template('admin/form_funcionario.html', usuario=None)

        usuario = Usuario(
            nome=nome, email=email, cargo=cargo,
            departamento=departamento, is_admin=is_admin,
        )
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        flash(f'Funcionário {nome} cadastrado com sucesso.', 'success')
        return redirect(url_for('admin.funcionarios'))

    return render_template('admin/form_funcionario.html', usuario=None)


@admin_bp.route('/funcionario/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_funcionario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nome = request.form.get('nome', '').strip()
        usuario.email = request.form.get('email', '').strip().lower()
        usuario.cargo = request.form.get('cargo', '').strip()
        usuario.departamento = request.form.get('departamento', '').strip()
        usuario.is_admin = request.form.get('is_admin') == 'on'
        usuario.ativo = request.form.get('ativo') == 'on'

        nova_senha = request.form.get('senha', '').strip()
        if nova_senha:
            if len(nova_senha) < 6:
                flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
                return render_template('admin/form_funcionario.html', usuario=usuario)
            usuario.set_senha(nova_senha)

        db.session.commit()
        flash('Funcionário atualizado com sucesso.', 'success')
        return redirect(url_for('admin.funcionarios'))

    return render_template('admin/form_funcionario.html', usuario=usuario)


@admin_bp.route('/relatorio')
@login_required
@admin_required
def relatorio():
    mes = request.args.get('mes', date.today().month, type=int)
    ano = request.args.get('ano', date.today().year, type=int)
    usuario_id = request.args.get('usuario_id', 0, type=int)

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    query = RegistroPonto.query.filter(
        RegistroPonto.data >= primeiro_dia,
        RegistroPonto.data <= ultimo_dia,
    )
    if usuario_id:
        query = query.filter_by(usuario_id=usuario_id)

    registros = query.order_by(
        RegistroPonto.usuario_id, RegistroPonto.data, RegistroPonto.data_hora
    ).all()

    por_usuario = {}
    for reg in registros:
        uid = reg.usuario_id
        if uid not in por_usuario:
            por_usuario[uid] = {'usuario': reg.usuario, 'dias': {}}
        d = reg.data
        if d not in por_usuario[uid]['dias']:
            por_usuario[uid]['dias'][d] = []
        por_usuario[uid]['dias'][d].append(reg)

    resumo = []
    for uid, dados in por_usuario.items():
        total = timedelta()
        for d, regs in dados['dias'].items():
            total += _calc_horas(regs)
        resumo.append({
            'usuario': dados['usuario'],
            'total_dias': len(dados['dias']),
            'total_horas': total,
        })

    resumo.sort(key=lambda x: x['usuario'].nome)
    usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all()

    return render_template('admin/relatorio.html',
                           resumo=resumo, mes=mes, ano=ano,
                           usuario_id=usuario_id, usuarios=usuarios,
                           label_tipo=RegistroPonto.label_tipo)


def _calc_horas(registros):
    total = timedelta()
    regs = sorted(registros, key=lambda r: r.data_hora)
    entrada = None
    for reg in regs:
        if reg.tipo in ('entrada', 'volta_almoco'):
            entrada = reg.data_hora
        elif reg.tipo in ('saida_almoco', 'saida'):
            if entrada:
                total += reg.data_hora - entrada
                entrada = None
    return total
