# Development Log — VYU Backend

## 14/08/2026

### 1. Análise Inicial e Escopo do Sprint 1
- Repositório clonado e estrutura inspecionada.
- Documentação técnica existente analisada:
  - `documentacao/database/restaurante.md`: Definição da entidade `restaurant` (ID, CNPJ, MANAGER_ID, CONTACT_PHONE, NAME, ADDRESS, SITE, INSTAGRAM, PATH_LOGO).
  - `documentacao/database/usuarios_app.md`: Definição da entidade `user_app` (ID, FIRST_NAME, LAST_NAME, PHONE_NUMBER, PATH_PHOTO, PASSWORD, LAST_LOGIN, EMAIL, USERNAME).
  - `documentacao/database/usuarios_restaurante.md`: Definição da entidade `user_manager` (ID, FIRST_NAME, LAST_NAME, PHONE_NUMBER, PATH_PHOTO, PASSWORD, LAST_LOGIN, EMAIL, USERNAME, RESTAURANT_COUNT computado).
  - `documentacao/requisitos/backend.md`: Arquitetura do Django com app central `MAIN` estruturado em camadas (`models/`, `serializers/`, `services/`, `views/`, `urls/`).
- Escopo estrito do Sprint 1: Foco exclusivo no fluxo de criação/autenticação de Gerente e Usuário, cadastro de Restaurantes pelo Gerente e busca pública de Restaurantes pelo Usuário.

---

### 2. Decisões Arquiteturais e de Segurança

#### A. Autenticação Dual-User via `djangorestframework-simplejwt`
- **Problema**: Existem duas entidades de usuário independentes (`UserManager` na tabela `user_manager` e `UserApp` na tabela `user_app`).
- **Decisão**: Utilização da biblioteca oficial `djangorestframework-simplejwt` sem geração manual de tokens.
- **Implementação**:
  - Tokens são assinados com HMAC-SHA256 utilizando `SECRET_KEY`.
  - Claims incluídos no token: `user_id`, `user_type` (`"MANAGER"` ou `"APP_USER"`), `username`, `email`.
  - Classe `CustomJWTAuthentication` intercepta a requisição, valida a assinatura criptográfica, extrai `user_type` e `user_id` e resolve a instância real para `request.user`.
  - O backend nunca confia em parâmetros de identidade enviados pelo cliente via payload ou headers.

#### B. Banco de Dados (MySQL) e Avaliação de Drivers
- **Problema**: O projeto exige MySQL para paridade com produção e futura migração para AWS RDS.
- **Avaliação de Drivers**:
  - `mysqlclient`: Baseado em C, alto desempenho, mas requer compilador C++ (MSVC no Windows) para build a partir do código fonte.
  - `PyMySQL`: 100% Python puro, estabilidade máxima, sem dependências nativas, compatibilidade total com o backend MySQL do Django via `pymysql.install_as_MySQLdb()`.
- **Decisão**: `PyMySQL` configurado como driver padrão em `vyu_core/__init__.py`, permitindo execução em Windows, Linux, containers e AWS RDS.
- **Configuração**: Todas as credenciais são gerenciadas via variáveis de ambiente (`DB_ENGINE=mysql`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

#### C. Unicidade de Identificadores (Email e Username)
- `user_manager` e `user_app` representam domínios distintos (Web Manager vs Mobile Consumer).
- A unicidade de `email` e `username` é restrita ao escopo de cada tabela (`unique=True` por tabela), permitindo que um gerente possa também criar conta de consumidor no app móvel.

#### D. Permissões e Prevenção contra IDOR/BOLA
- A permissão `IsRestaurantOwner` valida explicitamente **dois fatores**:
  1. O tipo do usuário autenticado (`isinstance(request.user, UserManager)` e `user_type == "MANAGER"`).
  2. A propriedade do recurso (`restaurant.manager_id == request.user.id`).
- Gerente A não consegue ler detalhes administrativos, alterar ou excluir restaurantes do Gerente B (retorna `403 Forbidden` / `404 Not Found`).

#### E. Proteção contra Mass Assignment
- Ao criar restaurante, o campo `manager_id` não é aceito via payload. O proprietário é atribuído estritamente via `request.user` autenticado no token JWT.
- Serializers definem `read_only_fields = ('id', 'created_at', 'updated_at', 'last_login')` para evitar sobreescrita acidental ou maliciosa de campos internos.

#### F. Separação de Endpoints Públicos e Administrativos
- **Endpoints Administrativos (`/api/restaurants/<id>/`, `/api/restaurants/`)**:
  - Restritos a gerentes autenticados (`IsManager`, `IsRestaurantOwner`).
  - Utilizam `RestaurantAdminResponseSerializer` (contém `cnpj`, `manager_id`, timestamps).
- **Endpoints Públicos (`/api/restaurants/public/`, `/api/restaurants/public/<id>/`)**:
  - Acessíveis a usuários do app e visitantes anônimos.
  - Utilizam `RestaurantPublicResponseSerializer` (retorna apenas nome, endereço, telefone de contato, site, instagram, logo; **nunca expõe `manager_id` ou dados administrativos**).

#### G. Throttling e Anti-Brute Force
- Throttles padrão (`AnonRateThrottle`, `UserRateThrottle`) e throttle dedicado para login (`LoginRateThrottle` com escopo `login: 10/minute`).
- Mensagens genéricas de erro de autenticação (`"Credenciais inválidas. Verifique seu e-mail/usuário e senha."`) para evitar enumeração de usuários.

#### H. CORS Restritivo
- `CORS_ALLOW_ALL_ORIGINS = False`. Origens permitidas são configuradas estritamente via whitelist por variável de ambiente (`CORS_ALLOWED_ORIGINS`).

#### I. Tratamento Seguro de Exceções
- Handler customizado (`custom_exception_handler`) que padroniza respostas de erro em JSON e oculta stack traces/caminhos internos em produção (`DEBUG=False`).

---

### 3. Arquivos Criados e Estrutura do Projeto

```text
restaurante-app-web/
├── .env.example                               # Modelo de variáveis de ambiente
├── .env                                       # Variáveis locais (ignorado no git)
├── .gitignore                                 # Configuração de arquivos ignorados
├── requirements.txt                           # Dependências do projeto
├── manage.py                                  # CLI do Django
├── DEVELOPMENT_LOG.md                         # Registro de desenvolvimento
├── README.md                                  # Documentação técnica completa
│
├── vyu_core/                                  # Configurações do projeto
│   ├── __init__.py                            # Instalação do PyMySQL como MySQLdb
│   ├── settings.py                            # Configurações (DRF, JWT, CORS, MySQL, Throttling)
│   ├── urls.py                                # Roteamento raiz para /api/
│   ├── wsgi.py                                # Interface WSGI
│   └── asgi.py                                # Interface ASGI
│
└── main/                                      # Aplicação central
    ├── __init__.py
    ├── apps.py                                # Configuração do app Main
    ├── admin.py                               # Registro no Django Admin
    ├── authentication.py                      # CustomJWTAuthentication (dual-user)
    ├── permissions.py                         # IsManager, IsAppUser, IsRestaurantOwner
    ├── throttling.py                          # LoginRateThrottle
    ├── exceptions.py                          # Handler de exceções seguro
    │
    ├── models/
    │   ├── __init__.py
    │   ├── base.py                            # TimeStampedModel
    │   ├── user_manager.py                    # Modelo UserManager (tabela user_manager)
    │   ├── user_app.py                        # Modelo UserApp (tabela user_app)
    │   └── restaurant.py                      # Modelo Restaurant (tabela restaurant)
    │
    ├── migrations/
    │   ├── 0001_initial.py                    # Migração inicial
    │
    ├── serializers/
    │   ├── __init__.py
    │   ├── auth_serializers.py                # Serializers de login e refresh
    │   ├── user_manager_serializers.py        # Serializers de cadastro, resposta e update do gerente
    │   ├── user_app_serializers.py            # Serializers de cadastro, resposta e update do app user
    │   └── restaurant_serializers.py          # Serializers admin e público de restaurante
    │
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py                    # Autenticação, emissão e refresh de JWT
    │   ├── user_manager_service.py            # Regras de negócio de gerente e hash de senha
    │   ├── user_app_service.py                # Regras de negócio de usuário do app e hash de senha
    │   └── restaurant_service.py              # Regras de CRUD, isolamento de dono e busca pública
    │
    ├── views/
    │   ├── __init__.py
    │   ├── auth_views.py                      # ManagerLoginView, UserAppLoginView, TokenRefreshView
    │   ├── user_manager_views.py              # ManagerRegistrationView, ManagerProfileView
    │   ├── user_app_views.py                  # UserAppRegistrationView, UserAppProfileView
    │   └── restaurant_views.py                # ManagerRestaurantListCreateView, Detail, Public views
    │
    ├── urls/
    │   ├── __init__.py
    │   ├── auth_urls.py                       # /api/auth/
    │   ├── user_manager_urls.py               # /api/managers/
    │   ├── user_app_urls.py                   # /api/users/
    │   ├── restaurant_urls.py                 # /api/restaurants/
    │   └── api_urls.py                        # Agregador central das rotas da API
    │
    └── tests/
        ├── __init__.py
        ├── test_user_manager.py               # 6 testes: registro, duplicatas, senhas, mass assignment
        ├── test_user_app.py                   # 4 testes: registro, duplicatas, isolamento de email, mass assignment
        ├── test_auth_jwt.py                   # 9 testes: login por email/user, anti-enumeração, claims, refresh, throttling
        ├── test_restaurant.py                 # 8 testes: CRUD do gerente, mass assignment, validações
        ├── test_authorization.py              # 5 testes: IDOR/BOLA Gerente A vs B, escalação de privilégios
        └── test_search.py                     # 5 testes: listagem pública, busca por nome/endereço, sanitização de schema
```

---

### 4. Bateria de Testes Automatizados Executada

Todos os 37 testes automatizados foram executados e passaram com **100% de sucesso**:

```text
Ran 37 tests in 34.782s

OK
Destroying test database for alias 'default'...
Found 37 test(s).
System check identified no issues (0 silenced).
```

#### Cobertura dos Testes:
1. `test_user_manager.py`:
   - Cadastro de gerente com sucesso e validação de hash PBKDF2.
   - Rejeição de e-mail duplicado (400).
   - Rejeição de username duplicado (400).
   - Rejeição de senha curta (400).
   - Rejeição de telefone inválido (400).
   - Proteção contra mass assignment (campos `id`, `restaurant_count` ignorados no payload).
2. `test_user_app.py`:
   - Cadastro de usuário consumidor com sucesso e validação de hash PBKDF2.
   - Rejeição de e-mail duplicado dentro da tabela `user_app`.
   - Permissão de compartilhamento de e-mail entre `user_manager` e `user_app` (tabelas distintas).
   - Proteção contra mass assignment.
3. `test_auth_jwt.py`:
   - Login de gerente com e-mail e senha -> Emissão de JWT access/refresh com claims `user_id`, `user_type: "MANAGER"`.
   - Login de gerente com username e senha.
   - Login de usuário do app com e-mail e senha -> Emissão de JWT com claims `user_id`, `user_type: "APP_USER"`.
   - Proteção anti-enumeração: senha incorreta retorna 401 genérico.
   - Proteção anti-enumeração: usuário inexistente retorna o mesmo 401 genérico.
   - Fluxo de refresh de token JWT.
   - Rejeição de acesso a endpoints protegidos sem token (401).
   - Rejeição de token forjado ou inválido (401).
   - Ativação e disparo do `LoginRateThrottle` com código 429 Too Many Requests.
4. `test_restaurant.py`:
   - Criação de restaurante por gerente autenticado.
   - Atribuição estrita do proprietário a partir do contexto JWT do servidor (ignora `manager_id` enviado no payload).
   - Listagem de restaurantes próprios do gerente (`GET /api/restaurants/`).
   - Obtenção de restaurante próprio (`GET /api/restaurants/<id>/`).
   - Atualização de restaurante próprio (`PUT /api/restaurants/<id>/`).
   - Proteção contra mass assignment na atualização (bloqueia alteração de `id` ou `manager_id`).
   - Exclusão de restaurante próprio (`DELETE /api/restaurants/<id>/`).
   - Validação de formato/tamanho de CNPJ (14 dígitos).
5. `test_authorization.py` (Suíte de Segurança IDOR/BOLA):
   - **IDOR 1**: Gerente A bloqueado ao tentar consultar restaurante do Gerente B (`403/404`).
   - **IDOR 2**: Gerente A bloqueado ao tentar alterar restaurante do Gerente B (`403/404`).
   - **IDOR 3**: Gerente A bloqueado ao tentar excluir restaurante do Gerente B (`403/404`).
   - **Escalação de Privilégio 1**: Usuário consumidor (App User) bloqueado ao tentar criar restaurante (`403`).
   - **Escalação de Privilégio 2**: Usuário consumidor bloqueado ao tentar acessar endpoint administrativo (`403`).
6. `test_search.py`:
   - Listagem pública de restaurantes sem autenticação.
   - Sanitização de resposta pública (garantia de que `manager_id`, `manager` e campos administrativos não são expostos).
   - Detalhe público de restaurante.
   - Busca por nome do restaurante (`?search=Sushi`).
   - Busca por endereço do restaurante (`?search=Pinheiros`).
   - Busca sem resultados retornando lista vazia com status 200.

---

### 5. Próximos Passos (Sprints Futuros)
- Configuração de ambiente de banco de dados MySQL em nuvem (AWS RDS).
- Desenvolvimento do Frontend Web (Angular + Angular Material) consumindo a API.
- Desenvolvimento do Frontend Mobile (React Native) consumindo a API.
- Evolução do modelo para entidade dedicada de Filas e Histórico (quando o escopo avançar para tempo real).
