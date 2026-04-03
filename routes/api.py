from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from extensions import db
from models import RegistroPonto, MoodLog, SessaoFoco, Usuario

api_bp = Blueprint('api', __name__)


@api_bp.route('/team-presence')
@login_required
def team_presence():
    """Retorna presença da equipe em tempo real."""
    hoje = date.today()
    usuarios = Usuario.query.filter_by(ativo=True).all()

    presenca = []
    for u in usuarios:
        regs = RegistroPonto.query.filter_by(
            usuario_id=u.id, data=hoje
        ).order_by(RegistroPonto.data_hora.asc()).all()

        tipos = [r.tipo for r in regs]
        if 'saida' in tipos:
            status = 'saiu'
        elif 'volta_almoco' in tipos:
            status = 'presente'
        elif 'saida_almoco' in tipos:
            status = 'almoco'
        elif 'entrada' in tipos:
            status = 'presente'
        else:
            status = 'ausente'

        ultima_acao = regs[-1].data_hora.strftime('%H:%M') if regs else None

        presenca.append({
            'nome': u.nome,
            'iniciais': u.iniciais,
            'cor': u.avatar_cor,
            'departamento': u.departamento,
            'status': status,
            'ultima_acao': ultima_acao,
        })

    return jsonify(presenca)


@api_bp.route('/mood-analytics')
@login_required
def mood_analytics():
    """Retorna dados de humor dos últimos 30 dias."""
    hoje = date.today()
    inicio = hoje - timedelta(days=30)

    moods = MoodLog.query.filter(
        MoodLog.usuario_id == current_user.id,
        MoodLog.data >= inicio,
    ).order_by(MoodLog.data.asc()).all()

    return jsonify({
        'datas': [m.data.strftime('%d/%m') for m in moods],
        'humor': [m.humor for m in moods],
        'energia': [m.energia for m in moods],
    })


@api_bp.route('/horas-semana')
@login_required
def horas_semana():
    """Retorna horas trabalhadas na semana atual."""
    hoje = date.today()
    inicio = hoje - timedelta(days=hoje.weekday())

    dados = []
    labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

    for i in range(7):
        d = inicio + timedelta(days=i)
        regs = RegistroPonto.query.filter_by(
            usuario_id=current_user.id, data=d
        ).order_by(RegistroPonto.data_hora.asc()).all()

        total = timedelta()
        entrada = None
        for reg in sorted(regs, key=lambda r: r.data_hora):
            if reg.tipo in ('entrada', 'volta_almoco'):
                entrada = reg.data_hora
            elif reg.tipo in ('saida_almoco', 'saida'):
                if entrada:
                    total += reg.data_hora - entrada
                    entrada = None

        dados.append(round(total.total_seconds() / 3600, 2))

    return jsonify({'labels': labels, 'dados': dados})


@api_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    current_user.tema = 'dark' if current_user.tema == 'light' else 'light'
    db.session.commit()
    return jsonify({'tema': current_user.tema})
