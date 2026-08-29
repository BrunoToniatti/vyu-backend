# VYU — Plataforma de Restaurantes (Backend API)

API RESTful desenvolvida em **Python + Django + Django REST Framework + MySQL**, responsável pela comunicação entre os gerentes de restaurantes (Web) e os usuários consumidores (Aplicativo Mobile).

---

## 1. Visão Geral e Arquitetura

O backend adota uma arquitetura em camadas estritas organizada dentro de uma aplicação central chamada `main`:

```text
restaurante-app-web/
├── .env.example                       # Modelo de variáveis de ambiente
├── requirements.txt                   # Dependências do projeto
├── manage.py                          # Utilitário de linha de comando Django
├── DEVELOPMENT_LOG.md                 # Histórico completo de desenvolvimento
├── vyu_core/                          # Configurações do projeto Django
│   ├── settings.py                    # Configuração geral (MySQL, JWT, CORS, Throttling)
│   ├── urls.py                        # Roteamento raiz para /api/
│   └── ...
└── main/                              # Aplicação central VYU
    ├── authentication.py              # Autenticador CustomJWTAuthentication
    ├── permissions.py                 # IsManager, IsAppUser, IsRestaurantOwner
    ├── throttling.py                  # LoginRateThrottle
    ├── exceptions.py                  # Handler seguro de exceções
    ├── models/                        # UserManager, UserApp, Restaurant
    ├── serializers/                   # Validação de entrada e sanitização de saída
    ├── services/                      # Regras de negócio e persistência
    ├── views/                         # Endpoints RESTful
    ├── urls/                          # Roteamento modular por categoria
    └── tests/                         # Suíte completa de testes automatizados
```

---

## 2. Tecnologias Utilizadas

- **Python 3.12+**
- **Django 5.2+**
- **Django REST Framework (DRF) 3.18+**
- **djangorestframework-simplejwt 5.5+** (Autenticação via JWT com HMAC-SHA256)
- **PyMySQL 1.2+** (Driver MySQL de alta estabilidade e portabilidade)
- **django-cors-headers 4.9+** (Controle estrito de CORS via whitelist)
- **python-dotenv 1.0+** (Gestão segura de variáveis de ambiente)

---

## 3. Instalação e Configuração

### Pré-requisitos
- Python 3.12 ou superior instalado.
- Servidor MySQL (local, container ou remoto/AWS RDS).

### Passo 1 — Clonar o Repositório e Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux/macOS:
source .venv/bin/activate
```

### Passo 2 — Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3 — Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e configure as credenciais:
```bash
cp .env.example .env
```

Exemplo de configuração no `.env`:
```env
# Django Settings
SECRET_KEY=sua-chave-secreta-forte-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database Configuration
DB_ENGINE=mysql
DB_NAME=vyu_db
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=127.0.0.1
DB_PORT=3306

# CORS Configuration (Strict Whitelist - Comma separated)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200,http://127.0.0.1:3000,http://127.0.0.1:4200

# Throttling
THROTTLE_LOGIN_RATE=10/minute
```

### Passo 4 — Executar Migrações
```bash
python manage.py migrate
```

### Passo 5 — Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver
```
O servidor estará acessível em `http://127.0.0.1:8000/`.

---

## 4. Endpoints da API

Todas as rotas estão centralizadas sob o prefixo `/api/`.

### 🔑 Autenticação (`/api/auth/`)

| Método | Rota | Descrição | Permissão | Throttle |
|---|---|---|---|---|
| `POST` | `/api/auth/manager/login/` | Login de Gerente (Web) | Aberto | `LoginRateThrottle` |
| `POST` | `/api/auth/app/login/` | Login de Usuário Consumidor (App) | Aberto | `LoginRateThrottle` |
| `POST` | `/api/auth/token/refresh/` | Atualização de Access Token JWT | Aberto | Padrão |

#### Exemplo de Payload de Login:
```json
{
  "identifier": "carlos.gerente@example.com",
  "password": "StrongPassword123!"
}
```

#### Exemplo de Resposta de Sucesso:
```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_type": "MANAGER",
    "user": {
      "id": 1,
      "first_name": "Carlos",
      "last_name": "Silva",
      "email": "carlos.gerente@example.com",
      "username": "carlos_gerente",
      "restaurant_count": 2
    }
  }
}
```

---

### 👔 Gerentes (`/api/managers/`)

| Método | Rota | Descrição | Permissão |
|---|---|---|---|
| `POST` | `/api/managers/` | Cadastro de novo Gerente | Aberto |
| `GET` | `/api/managers/me/` | Obter perfil do Gerente autenticado | `IsManager` |
| `PUT` | `/api/managers/me/` | Atualizar perfil do Gerente autenticado | `IsManager` |

---

### 📱 Usuários do App (`/api/users/`)

| Método | Rota | Descrição | Permissão |
|---|---|---|---|
| `POST` | `/api/users/` | Cadastro de novo Usuário Consumidor | Aberto |
| `GET` | `/api/users/me/` | Obter perfil do Usuário autenticado | `IsAppUser` |
| `PUT` | `/api/users/me/` | Atualizar perfil do Usuário autenticado | `IsAppUser` |

---

### 🍽️ Restaurantes — Gestão Administrativa (`/api/restaurants/`)

| Método | Rota | Descrição | Permissão |
|---|---|---|---|
| `POST` | `/api/restaurants/` | Criar novo restaurante | `IsManager` |
| `GET` | `/api/restaurants/` | Listar restaurantes do gerente logado | `IsManager` |
| `GET` | `/api/restaurants/<id>/` | Obter detalhes administrativos de restaurante próprio | `IsManager` + `IsRestaurantOwner` |
| `PUT` | `/api/restaurants/<id>/` | Atualizar restaurante próprio | `IsManager` + `IsRestaurantOwner` |
| `DELETE` | `/api/restaurants/<id>/` | Excluir restaurante próprio | `IsManager` + `IsRestaurantOwner` |

#### Exemplo de Payload para Criação de Restaurante:
```json
{
  "name": "Bistrô Paris 6",
  "cnpj": "12345678000195",
  "contact_phone": "1130004000",
  "address": "Rua Haddock Lobo, 1240, Jardins, São Paulo - SP",
  "site": "https://bistroparis.example.com",
  "instagram": "@bistroparis",
  "path_logo": "https://storage.example.com/logos/paris6.png"
}
```
> **Nota de Segurança**: O campo `manager_id` não é aceito no payload. O proprietário do restaurante é atribuído de forma estrita no servidor a partir do token JWT verificado.

---

### 🔍 Restaurantes — Consulta Pública (`/api/restaurants/public/`)

| Método | Rota | Descrição | Permissão |
|---|---|---|---|
| `GET` | `/api/restaurants/public/` | Listar restaurantes públicos (filtro via `?search=`) | Aberto / App User |
| `GET` | `/api/restaurants/public/<id>/` | Obter perfil público de um restaurante | Aberto / App User |

#### Exemplo de Resposta Pública:
```json
{
  "status": "success",
  "status_code": 200,
  "data": {
    "id": 1,
    "name": "Bistrô Paris 6",
    "address": "Rua Haddock Lobo, 1240, Jardins, São Paulo - SP",
    "contact_phone": "1130004000",
    "site": "https://bistroparis.example.com",
    "instagram": "@bistroparis",
    "path_logo": "https://storage.example.com/logos/paris6.png"
  }
}
```
> **Nota de Privacidade**: A resposta pública **nunca expõe** `manager_id`, dados do proprietário, CNPJ ou campos internos do sistema.

---

## 5. Diretrizes de Segurança Implementadas

1. **Hashing Criptográfico de Senhas**: As senhas são armazenadas exclusivamente utilizando o algoritmo `PBKDF2PasswordHasher` com SHA-256 do Django (`set_password`/`check_password`). Senhas em texto puro nunca são salvas ou registradas em logs.
2. **Sanitização de Serializers**: Campos de senha são estritamente `write_only=True` e jamais são retornados em nenhuma resposta HTTP da API.
3. **Autenticação JWT com Resolução Segura**: O backend assina e valida tokens JWT via SimpleJWT, extraindo `user_id` e `user_type` diretamente das claims verificadas.
4. **Isolamento de Recursos (Proteção contra IDOR / BOLA)**: A classe de permissão `IsRestaurantOwner` valida simultaneamente o tipo do usuário (`UserManager`) e a correspondência do `manager_id`. Gerente A é terminantemente impedido de consultar, editar ou excluir dados do Gerente B.
5. **Proteção contra Mass Assignment**: Serializers definem `read_only_fields` para identificadores, timestamps (`created_at`, `updated_at`) e relações de posse.
6. **Proteção Anti-Enumeração e Anti-Brute Force**: Respostas de login retornam mensagens genéricas de falha tanto para usuários inexistentes quanto para senhas incorretas, combinadas com taxa de requisição restritiva (`LoginRateThrottle`).
7. **CORS em Whitelist Estrita**: Origens permitidas são configuradas individualmente via variável de ambiente, com `CORS_ALLOW_ALL_ORIGINS = False`.

---

## 6. Execução dos Testes Automatizados

Para executar toda a suíte de testes:

```bash
python manage.py test main.tests
```

Para executar suítes específicas:
```bash
# Testes de Gerente
python manage.py test main.tests.test_user_manager

# Testes de Usuário Consumidor
python manage.py test main.tests.test_user_app

# Testes de Autenticação JWT e Throttling
python manage.py test main.tests.test_auth_jwt

# Testes de CRUD de Restaurante
python manage.py test main.tests.test_restaurant

# Testes de Segurança contra IDOR/BOLA e Escalação de Privilégios
python manage.py test main.tests.test_authorization

# Testes de Busca Pública de Restaurantes
python manage.py test main.tests.test_search
```

---

## 7. Registro de Desenvolvimento

Consulte o arquivo [`DEVELOPMENT_LOG.md`](file:///c:/Users/joaop/OneDrive/Área%20de%20Trabalho/VYU/DEVELOPMENT_LOG.md) para o histórico detalhado de todas as alterações, justificativas arquiteturais e decisões técnicas tomadas durante o projeto.
