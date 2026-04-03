from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from extensions import db
from models import RegistroPonto, MoodLog, Conquista, UserConquista, SessaoFoco, Usuario

ponto_bp = Blueprint('ponto', __name__)


@ponto_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('ponto.dashboard'))
    return redirect(url_for('auth.login'))


@ponto_bp.route('/dashboard')
@login_required
def dashboard():
    hoje = date.today()
    registros_hoje = RegistroPonto.query.filter_by(
        usuario_id=current_user.id, data=hoje
    ).order_by(RegistroPonto.data_hora.asc()).all()

    tipos_registrados = [r.tipo for r in registros_hoje]
    proximo_tipo = _proximo_tipo(tipos_registrados)
    horas_trabalhadas = _calcular_horas(registros_hoje)

    mood_hoje = MoodLog.query.filter_by(
        usuario_id=current_user.id, data=hoje
    ).first()

    ultimos_dias = []
    for i in range(1, 8):
        d = hoje - timedelta(days=i)
        regs = RegistroPonto.query.filter_by(
            usuario_id=current_user.id, data=d
        ).order_by(RegistroPonto.data_hora.asc()).all()
        if regs:
            ultimos_dias.append({
                'data': d,
                'registros': regs,
                'horas': _calcular_horas(regs),
            })

    conquistas = UserConquista.query.filter_by(
        usuario_id=current_user.id
    ).order_by(UserConquista.desbloqueada_em.desc()).limit(5).all()

    wellness = current_user.wellness_score()

    sessoes_foco_hoje = SessaoFoco.query.filter_by(
        usuario_id=current_user.id, data=hoje, completada=True
    ).count()

    return render_template('dashboard.html',
                           registros_hoje=registros_hoje,
                           proximo_tipo=proximo_tipo,
                           horas_trabalhadas=horas_trabalhadas,
                           ultimos_dias=ultimos_dias,
                           hoje=hoje,
                           mood_hoje=mood_hoje,
                           conquistas=conquistas,
                           wellness=wellness,
                           sessoes_foco_hoje=sessoes_foco_hoje,
                           label_tipo=RegistroPonto.label_tipo,
                           icone_tipo=RegistroPonto.icone_tipo)


@ponto_bp.route('/registrar', methods=['POST'])
@login_required
def registrar():
    hoje = date.today()
    agora = datetime.now()
    observacao = request.form.get('observacao', '').strip()

    registros_hoje = RegistroPonto.query.filter_by(
        usuario_id=current_user.id, data=hoje
    ).order_by(RegistroPonto.data_hora.asc()).all()

    tipos_registrados = [r.tipo for r in registros_hoje]
    proximo_tipo = _proximo_tipo(tipos_registrados)

    if proximo_tipo is None:
        flash('Todos os registros do dia já foram realizados.', 'warning')
        return redirect(url_for('ponto.dashboard'))

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    registro = RegistroPonto(
        usuario_id=current_user.id,
        tipo=proximo_tipo,
        data_hora=agora,
        data=hoje,
        observacao=observacao,
        ip_address=ip,
    )
    db.session.add(registro)

    # Gamificação: XP por registro
    current_user.xp += 5

    # Streak logic
    if proximo_tipo == 'entrada':
        ontem = hoje - timedelta(days=1)
        if current_user.ultimo_ponto_data == ontem:
            current_user.streak_atual += 1
        elif current_user.ultimo_ponto_data != hoje:
            current_user.streak_atual = 1
        current_user.ultimo_ponto_data = hoje
        if current_user.streak_atual > current_user.maior_streak:
            current_user.maior_streak = current_user.streak_atual

    db.session.commit()

    # Check conquistas
    _verificar_conquistas(current_user, agora)

    flash(f'{RegistroPonto.label_tipo(proximo_tipo)} registrada às {agora.strftime("%H:%M:%S")}. +5 XP', 'success')
    return redirect(url_for('ponto.dashboard'))


@ponto_bp.route('/mood', methods=['POST'])
@login_required
def registrar_mood():
    hoje = date.today()
    humor = request.form.get('humor', 3, type=int)
    energia = request.form.get('energia', 3, type=int)
    nota = request.form.get('nota', '').strip()

    humor = max(1, min(5, humor))
    energia = max(1, min(5, energia))

    mood = MoodLog.query.filter_by(usuario_id=current_user.id, data=hoje).first()
    if mood:
        mood.humor = humor
        mood.energia = energia
        mood.nota = nota
    else:
        mood = MoodLog(
            usuario_id=current_user.id,
            data=hoje,
            humor=humor,
            energia=energia,
            nota=nota,
        )
        db.session.add(mood)
        current_user.xp += 3

    db.session.commit()
    flash('Humor registrado! +3 XP', 'success')
    return redirect(url_for('ponto.dashboard'))


@ponto_bp.route('/foco/completar', methods=['POST'])
@login_required
def completar_foco():
    hoje = date.today()
    duracao = request.form.get('duracao', 25, type=int)
    tipo = request.form.get('tipo', 'foco')

    sessao = SessaoFoco(
        usuario_id=current_user.id,
        duracao_minutos=duracao,
        completada=True,
        tipo=tipo,
        data=hoje,
    )
    db.session.add(sessao)

    if tipo == 'foco':
        current_user.xp += 10
        flash('Sessão de foco completada! +10 XP', 'success')
    else:
        flash('Pausa completada!', 'info')

    db.session.commit()
    _verificar_conquistas(current_user, datetime.now())
    return redirect(url_for('ponto.dashboard'))


@ponto_bp.route('/historico')
@login_required
def historico():
    mes = request.args.get('mes', date.today().month, type=int)
    ano = request.args.get('ano', date.today().year, type=int)

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    registros = RegistroPonto.query.filter(
        RegistroPonto.usuario_id == current_user.id,
        RegistroPonto.data >= primeiro_dia,
        RegistroPonto.data <= ultimo_dia,
    ).order_by(RegistroPonto.data.asc(), RegistroPonto.data_hora.asc()).all()

    moods = MoodLog.query.filter(
        MoodLog.usuario_id == current_user.id,
        MoodLog.data >= primeiro_dia,
        MoodLog.data <= ultimo_dia,
    ).all()
    moods_por_data = {m.data: m for m in moods}

    dias = {}
    for reg in registros:
        d = reg.data
        if d not in dias:
            dias[d] = []
        dias[d].append(reg)

    resumo_dias = []
    total_horas = timedelta()
    horas_por_dia = []
    humor_por_dia = []
    datas_labels = []

    for d in sorted(dias.keys()):
        horas = _calcular_horas(dias[d])
        total_horas += horas
        mood = moods_por_data.get(d)
        resumo_dias.append({
            'data': d,
            'registros': dias[d],
            'horas': horas,
            'mood': mood,
        })
        horas_por_dia.append(round(horas.total_seconds() / 3600, 2))
        humor_por_dia.append(mood.humor if mood else None)
        datas_labels.append(d.strftime('%d/%m'))

    carga_horaria = current_app.config['CARGA_HORARIA_DIARIA']
    dias_uteis = sum(1 for d in resumo_dias if d['data'].weekday() < 5)

    todas_conquistas = Conquista.query.all()
    user_conquistas = {uc.conquista_id for uc in
                       UserConquista.query.filter_by(usuario_id=current_user.id).all()}

    return render_template('historico.html',
                           resumo_dias=resumo_dias,
                           mes=mes, ano=ano,
                           total_horas=total_horas,
                           dias_uteis=dias_uteis,
                           carga_horaria=carga_horaria,
                           horas_por_dia=horas_por_dia,
                           humor_por_dia=humor_por_dia,
                           datas_labels=datas_labels,
                           todas_conquistas=todas_conquistas,
                           user_conquistas=user_conquistas,
                           label_tipo=RegistroPonto.label_tipo)


@ponto_bp.route('/conquistas')
@login_required
def conquistas():
    todas = Conquista.query.all()
    desbloqueadas = {uc.conquista_id: uc.desbloqueada_em for uc in
                     UserConquista.query.filter_by(usuario_id=current_user.id).all()}
    return render_template('conquistas.html',
                           todas=todas,
                           desbloqueadas=desbloqueadas)


def _proximo_tipo(tipos_registrados):
    ordem = RegistroPonto.tipos_ordenados()
    for tipo in ordem:
        if tipo not in tipos_registrados:
            return tipo
    return None


def _calcular_horas(registros):
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


def _verificar_conquistas(usuario, agora):
    def _dar_conquista(codigo):
        conquista = Conquista.query.filter_by(codigo=codigo).first()
        if not conquista:
            return
        existe = UserConquista.query.filter_by(
            usuario_id=usuario.id, conquista_id=conquista.id
        ).first()
        if not existe:
            uc = UserConquista(usuario_id=usuario.id, conquista_id=conquista.id)
            db.session.add(uc)
            usuario.xp += conquista.xp_bonus
            db.session.commit()

    total_registros = RegistroPonto.query.filter_by(usuario_id=usuario.id, tipo='entrada').count()
    if total_registros >= 1:
        _dar_conquista('primeiro_ponto')
    if total_registros >= 60:
        _dar_conquista('veterano')

    if usuario.streak_atual >= 5:
        _dar_conquista('streak_5')
    if usuario.streak_atual >= 10:
        _dar_conquista('streak_10')
    if usuario.streak_atual >= 30:
        _dar_conquista('streak_30')

    if agora.hour < 9:
        entradas_cedo = RegistroPonto.query.filter(
            RegistroPonto.usuario_id == usuario.id,
            RegistroPonto.tipo == 'entrada',
            db.extract('hour', RegistroPonto.data_hora) < 9,
        ).count()
        if entradas_cedo >= 5:
            _dar_conquista('pontual_5')

    if agora.hour < 7 or (agora.hour == 7 and agora.minute < 30):
        _dar_conquista('madrugador')

    sessoes_foco = SessaoFoco.query.filter_by(
        usuario_id=usuario.id, completada=True, tipo='foco'
    ).count()
    if sessoes_foco >= 10:
        _dar_conquista('foco_mestre')

    if usuario.xp >= 100:
        _dar_conquista('centuriao')
