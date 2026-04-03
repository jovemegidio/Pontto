from datetime import datetime, date, time, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    cargo = db.Column(db.String(100), default='')
    departamento = db.Column(db.String(100), default='')
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_cor = db.Column(db.String(7), default='#2563eb')
    xp = db.Column(db.Integer, default=0)
    streak_atual = db.Column(db.Integer, default=0)
    maior_streak = db.Column(db.Integer, default=0)
    ultimo_ponto_data = db.Column(db.Date, nullable=True)
    tema = db.Column(db.String(10), default='light')

    registros = db.relationship('RegistroPonto', backref='usuario', lazy='dynamic',
                                order_by='RegistroPonto.data_hora.desc()')
    moods = db.relationship('MoodLog', backref='usuario', lazy='dynamic',
                            order_by='MoodLog.data.desc()')
    conquistas = db.relationship('UserConquista', backref='usuario', lazy='dynamic')
    sessoes_foco = db.relationship('SessaoFoco', backref='usuario', lazy='dynamic')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def nivel(self):
        return self.xp // 100 + 1

    @property
    def xp_proximo_nivel(self):
        return 100 - (self.xp % 100)

    @property
    def xp_percentual(self):
        return (self.xp % 100)

    @property
    def iniciais(self):
        partes = self.nome.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nome[:2].upper()

    def wellness_score(self):
        """Calcula score de bem-estar baseado em padrões de trabalho (0-100)."""
        hoje = date.today()
        inicio = hoje - timedelta(days=30)
        registros = RegistroPonto.query.filter(
            RegistroPonto.usuario_id == self.id,
            RegistroPonto.data >= inicio
        ).all()

        if not registros:
            return 50

        score = 70
        moods_recentes = MoodLog.query.filter(
            MoodLog.usuario_id == self.id,
            MoodLog.data >= inicio
        ).all()

        if moods_recentes:
            avg_humor = sum(m.humor for m in moods_recentes) / len(moods_recentes)
            avg_energia = sum(m.energia for m in moods_recentes) / len(moods_recentes)
            score += (avg_humor - 3) * 5 + (avg_energia - 3) * 5

        score += min(self.streak_atual, 10) * 1
        return max(0, min(100, int(score)))

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class RegistroPonto(db.Model):
    __tablename__ = 'registros_ponto'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data = db.Column(db.Date, nullable=False, default=date.today, index=True)
    observacao = db.Column(db.String(500), default='')
    ip_address = db.Column(db.String(45), default='')

    __table_args__ = (
        db.Index('idx_usuario_data', 'usuario_id', 'data'),
    )

    def __repr__(self):
        return f'<Registro {self.tipo} - {self.data_hora}>'

    @staticmethod
    def tipos_ordenados():
        return ['entrada', 'saida_almoco', 'volta_almoco', 'saida']

    @staticmethod
    def label_tipo(tipo):
        labels = {
            'entrada': 'Entrada',
            'saida_almoco': 'Saída Almoço',
            'volta_almoco': 'Volta Almoço',
            'saida': 'Saída',
        }
        return labels.get(tipo, tipo)

    @staticmethod
    def icone_tipo(tipo):
        icones = {
            'entrada': 'bi-box-arrow-in-right',
            'saida_almoco': 'bi-cup-hot',
            'volta_almoco': 'bi-arrow-return-left',
            'saida': 'bi-box-arrow-right',
        }
        return icones.get(tipo, 'bi-clock')


class MoodLog(db.Model):
    __tablename__ = 'mood_logs'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False, default=date.today, index=True)
    humor = db.Column(db.Integer, nullable=False, default=3)  # 1-5
    energia = db.Column(db.Integer, nullable=False, default=3)  # 1-5
    nota = db.Column(db.String(300), default='')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'data', name='uq_mood_usuario_data'),
    )

    @staticmethod
    def emoji_humor(val):
        emojis = {1: '😞', 2: '😕', 3: '😐', 4: '😊', 5: '😄'}
        return emojis.get(val, '😐')

    @staticmethod
    def emoji_energia(val):
        emojis = {1: '🔋', 2: '🪫', 3: '⚡', 4: '🔥', 5: '🚀'}
        return emojis.get(val, '⚡')

    @staticmethod
    def label_humor(val):
        labels = {1: 'Muito Baixo', 2: 'Baixo', 3: 'Normal', 4: 'Bom', 5: 'Ótimo'}
        return labels.get(val, 'Normal')


class Conquista(db.Model):
    __tablename__ = 'conquistas'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    icone = db.Column(db.String(10), default='🏆')
    xp_bonus = db.Column(db.Integer, default=50)
    cor = db.Column(db.String(7), default='#f59e0b')

    DEFINICOES = [
        ('primeiro_ponto', 'Primeiro Passo', 'Registrou seu primeiro ponto', '👣', 10, '#22c55e'),
        ('streak_5', 'Constância', '5 dias consecutivos no ponto', '🔥', 25, '#f59e0b'),
        ('streak_10', 'Dedicação', '10 dias consecutivos no ponto', '💪', 50, '#ef4444'),
        ('streak_30', 'Inabalável', '30 dias consecutivos no ponto', '🏆', 150, '#8b5cf6'),
        ('pontual_5', 'Pontualidade', '5 entradas antes das 9:00', '⏰', 30, '#3b82f6'),
        ('foco_mestre', 'Mestre do Foco', 'Completou 10 sessões de foco', '🎯', 40, '#ec4899'),
        ('madrugador', 'Madrugador', 'Entrada antes das 7:30', '🌅', 20, '#f97316'),
        ('equilibrio', 'Equilíbrio', 'Wellness score acima de 85 por 7 dias', '🧘', 60, '#14b8a6'),
        ('centuriao', 'Centurião', 'Alcançou 100 XP', '💯', 25, '#6366f1'),
        ('veterano', 'Veterano', 'Registrou ponto por 60 dias', '🎖️', 100, '#a855f7'),
    ]


class UserConquista(db.Model):
    __tablename__ = 'user_conquistas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    conquista_id = db.Column(db.Integer, db.ForeignKey('conquistas.id'), nullable=False)
    desbloqueada_em = db.Column(db.DateTime, default=datetime.utcnow)

    conquista = db.relationship('Conquista')

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'conquista_id', name='uq_user_conquista'),
    )


class SessaoFoco(db.Model):
    __tablename__ = 'sessoes_foco'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duracao_minutos = db.Column(db.Integer, nullable=False, default=25)
    completada = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(20), default='foco')  # 'foco', 'pausa_curta', 'pausa_longa'
    data = db.Column(db.Date, nullable=False, default=date.today)


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
