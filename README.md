<div align="center">

<br>

<img src="https://img.shields.io/badge/Pont·to-Sistema%20Inteligente%20de%20Ponto-6366f1?style=for-the-badge&labelColor=0f172a" alt="Pontto"/>

<br><br>

<p>
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/flask-3.0-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white" alt="Bootstrap"/>
  <img src="https://img.shields.io/badge/chart.js-4.4-FF6384?style=flat-square&logo=chartdotjs&logoColor=white" alt="Chart.js"/>
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/license-MIT-10b981?style=flat-square" alt="License"/>
</p>

<p><strong>Sistema de ponto eletrônico com gamificação, wellness tracking e analytics em tempo real.</strong></p>

<p><em>Aplicação web full-stack desenvolvida com Python/Flask que transforma o controle de jornada em uma<br>experiência inteligente — combinando registro de ponto, mood tracker, focus timer (Pomodoro),<br>conquistas gamificadas, wellness score e dashboards administrativos em tempo real.</em></p>

<p>
  <a href="https://jovemegidio.github.io/Pontto/">
    <img src="https://img.shields.io/badge/▶%20VER%20DEMO%20ONLINE-6366f1?style=for-the-badge&logoColor=white" alt="Demo"/>
  </a>
</p>

<br>

</div>

---

## Sobre o Projeto

**Pontto** é um sistema de ponto eletrônico completo que transforma o registro de jornada em uma experiência inteligente. Além do controle de entrada e saída, o sistema monitora o bem-estar dos colaboradores, gamifica a consistência e entrega analytics acionáveis para gestores.

Projetado para uso diário em equipes reais, com interface responsiva, dark mode e arquitetura modular.

<br>

## Diferenciais

O Pontto combina funcionalidades que não existem juntas em nenhum sistema de ponto do mercado:

| Funcionalidade | Descrição |
|:---|:---|
| <img src="https://img.shields.io/badge/-Mood%20Tracker-ec4899?style=flat-square"/> | Registro diário de humor e energia para prevenção de burnout |
| <img src="https://img.shields.io/badge/-Gamificação-f59e0b?style=flat-square"/> | Sistema de XP, níveis e streaks por consistência de ponto |
| <img src="https://img.shields.io/badge/-Conquistas-8b5cf6?style=flat-square"/> | 10 badges desbloqueáveis com critérios progressivos |
| <img src="https://img.shields.io/badge/-Wellness%20Score-10b981?style=flat-square"/> | Índice 0–100 calculado por humor, energia e padrões de jornada |
| <img src="https://img.shields.io/badge/-Focus%20Timer-3b82f6?style=flat-square"/> | Pomodoro integrado com XP por sessão completada |
| <img src="https://img.shields.io/badge/-Team%20Heatmap-6366f1?style=flat-square"/> | Presença da equipe em tempo real no painel admin |
| <img src="https://img.shields.io/badge/-Analytics-ef4444?style=flat-square"/> | Gráficos de horas semanais, tendência de humor e saldo mensal |
| <img src="https://img.shields.io/badge/-Dark%20Mode-0f172a?style=flat-square"/> | Tema claro/escuro persistente por usuário |

<br>

## Stack Técnica

```
Backend       Python 3.10+ · Flask 3.0 · SQLAlchemy · Flask-Login
Frontend      Bootstrap 5.3 · Chart.js 4.4 · Inter (Google Fonts)
Banco         SQLite (desenvolvimento) — compatível com PostgreSQL
Auth          Werkzeug (bcrypt hashing) · sessões seguras
Arquitetura   Blueprints · MVC · API REST interna
```

<br>

## Estrutura do Projeto

```
Pontto/
├── app.py                 # Factory da aplicação
├── config.py              # Configurações via variáveis de ambiente
├── extensions.py          # Instâncias de SQLAlchemy e LoginManager
├── models.py              # Modelos: Usuario, RegistroPonto, MoodLog, Conquista, SessaoFoco
├── run.py                 # Entrypoint
├── requirements.txt       # Dependências Python
├── .env.example           # Template de variáveis de ambiente
│
├── routes/
│   ├── auth.py            # Login, logout, perfil
│   ├── ponto.py           # Dashboard, registro, mood, foco, histórico, conquistas
│   ├── admin.py           # Painel admin, funcionários, relatórios
│   └── api.py             # Endpoints JSON: presença, analytics, tema
│
├── templates/
│   ├── base.html          # Layout principal com navbar e tema
│   ├── login.html         # Tela de login
│   ├── dashboard.html     # Dashboard com clock, stats, mood, foco, gráficos
│   ├── historico.html     # Histórico mensal com charts
│   ├── perfil.html        # Perfil do colaborador
│   ├── conquistas.html    # Galeria de conquistas
│   └── admin/
│       ├── painel.html    # Painel administrativo com team heatmap
│       ├── funcionarios.html
│       ├── form_funcionario.html
│       └── relatorio.html
│
└── docs/                  # GitHub Pages (demo estática)
    └── index.html
```

<br>

## Funcionalidades Detalhadas

### Para Colaboradores

- **Registro de ponto em 1 clique** — 4 batidas diárias (Entrada, Saída Almoço, Volta Almoço, Saída)
- **Relógio em tempo real** com o próximo tipo de registro destacado
- **Mood & Energy Tracker** — seleção visual de humor (5 níveis) e energia a cada dia
- **Focus Timer** — Pomodoro configurável (25/5/15 min) com XP automático
- **Histórico mensal** com gráficos de horas e tendência de humor
- **Saldo de horas** calculado automaticamente contra carga horária esperada
- **Sistema de XP** — +5 XP por batida, +3 XP por mood, +10 XP por sessão de foco
- **Streaks** — dias consecutivos de ponto com indicador visual
- **10 Conquistas** — Primeiro Passo, Constância, Dedicação, Inabalável, Pontualidade, Mestre do Foco, Madrugador, Equilíbrio, Centurião, Veterano
- **Wellness Score** — índice de 0 a 100 que cruza humor, energia e padrões
- **Dark/Light mode** persistente

### Para Administradores

- **Dashboard executivo** — funcionários ativos, presentes hoje, total de registros
- **Team Presence Heatmap** — status em tempo real de cada colaborador (presente, almoço, saiu, ausente)
- **CRUD de funcionários** — cadastro, edição, ativação/desativação, definição de admin
- **Relatório mensal** — horas por funcionário, dias trabalhados, wellness score
- **Filtros por mês, ano e funcionário**

<br>

## API Endpoints

| Método | Rota | Descrição |
|:---|:---|:---|
| `GET` | `/api/team-presence` | Status de presença de toda a equipe |
| `GET` | `/api/mood-analytics` | Dados de humor dos últimos 30 dias |
| `GET` | `/api/horas-semana` | Horas trabalhadas na semana corrente |
| `POST` | `/api/toggle-theme` | Alterna dark/light mode do usuário |

<br>

## Modelo de Dados

```
Usuario ──┬── RegistroPonto (entrada, saída_almoço, volta_almoço, saída)
           ├── MoodLog (humor 1-5, energia 1-5, nota)
           ├── UserConquista ── Conquista (10 tipos)
           └── SessaoFoco (pomodoro, pausas)
```

<br>

## Configuração

**1.** Copie o template de variáveis de ambiente:

```
cp .env.example .env
```

**2.** Edite o `.env` com suas configurações:

```
SECRET_KEY=sua-chave-secreta
NOME_EMPRESA=Nome da Empresa
CARGA_HORARIA_DIARIA=8
```

**3.** Instale as dependências:

```
pip install -r requirements.txt
```

**4.** Execute:

```
python run.py
```

**5.** Acesse `http://localhost:5000`

> **Credenciais padrão:** `admin@empresa.com` / `admin123`

<br>

## Screenshots

> Acesse a [demo online](https://jovemegidio.github.io/Pontto/) para ver a interface completa.

<br>

## Roadmap

- [ ] Exportação para PDF/Excel
- [ ] Notificações por e-mail
- [ ] Geolocalização na batida
- [ ] PWA (Progressive Web App)
- [ ] Integração com Slack/Teams
- [ ] Deploy com Docker

<br>

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.

<br>

---

<div align="center">
  <p>
    <sub>Desenvolvido por <strong><a href="https://github.com/jovemegidio">jovemegidio</a></strong></sub>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/Powered%20by-Flask-000000?style=flat-square&logo=flask&logoColor=white"/>
  </p>
</div>
