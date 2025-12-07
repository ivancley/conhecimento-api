# Conhecimento API

## Introdução

Conhecimento API é uma aplicação Django REST Framework que implementa um sistema de gerenciamento de conhecimento baseado em RAG (Retrieval-Augmented Generation). A aplicação permite que usuários façam upload de documentos PDF, que são processados e indexados em um banco de dados vetorial (ChromaDB) para posterior consulta através de um sistema de perguntas e respostas.

O sistema utiliza processamento assíncrono com Celery para ingestão de documentos e integração com modelos de linguagem da OpenAI para geração de respostas contextualizadas baseadas no conteúdo dos documentos enviados.

## Tecnologias Utilizadas

### Backend

- **Django 6.0** - Framework web Python
- **Django REST Framework** - Construção de APIs REST
- **Djoser** - Autenticação e gerenciamento de usuários
- **JWT (JSON Web Tokens)** - Autenticação baseada em tokens
- **Celery** - Processamento assíncrono de tarefas
- **Redis** - Broker de mensagens para Celery

### Banco de Dados

- **MySQL 8.0** - Banco de dados relacional principal
- **ChromaDB** - Banco de dados vetorial para armazenamento de embeddings
- **Redis** - Cache e broker de mensagens

### IA e Processamento

- **OpenAI API** - Modelos GPT-4o-mini para geração de respostas e text-embedding-3-small para embeddings
- **LlamaIndex** - Framework para construção de pipelines RAG
- **pypdf** - Extração de texto de arquivos PDF

### Documentação

- **drf-spectacular** - Geração automática de documentação OpenAPI/Swagger

## Pré-requisitos

- Python 3.13 ou superior
- Docker e Docker Compose
- Conta OpenAI com API key
- Git

## Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone git@github.com:ivancley/conhecimento-api.git
cd conhecimento-api
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Django
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=7
ALGORITHM=HS256
SIGNING_KEY=sua-signing-key-aqui

# MySQL (já configurado para conectar ao container)
MYSQL_ENGINE=django.db.backends.mysql
MYSQL_DATABASE=conhecimento
MYSQL_USER=conhecimento_user
MYSQL_PASSWORD=Senha@123
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sua-openai-api-key-aqui

# ChromaDB (já configurado para conectar ao container)
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
```

**Importante:** As configurações de MySQL, Redis e ChromaDB no arquivo `.env` já estão apontando para os containers do Docker. Não é necessário alterar essas configurações se você estiver usando os containers.

### 5. Suba os containers Docker

Execute o comando para subir todos os serviços necessários:

```bash
docker-compose up -d
```

Isso irá iniciar os seguintes serviços:

- **MySQL** na porta 3306
- **ChromaDB** na porta 8001
- **Redis** na porta 6379

### 6. Execute as migrações

```bash
python manage.py migrate
```

### 7. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 8. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

A aplicação estará disponível em `http://localhost:8000`

### 9. Inicie o worker do Celery (em outro terminal)

```bash
celery -A config worker --loglevel=info
```

## Estrutura do Projeto

```
conhecimento-api/
├── apps/
│   ├── accounts/          # Gerenciamento de usuários e autenticação
│   └── knowledge/         # Módulo principal de conhecimentos e mensagens
│       ├── services/      # Serviços de IA e RAG
│       ├── models.py      # Modelos de dados
│       ├── views.py       # ViewSets da API
│       ├── serializers.py # Serializers DRF
│       └── tasks.py        # Tarefas assíncronas Celery
├── config/                # Configurações do Django
├── media/                 # Arquivos enviados pelos usuários
├── docker-compose.yml     # Configuração dos containers
└── requirements.txt       # Dependências Python
```

## Endpoints da API

### Autenticação

- `POST /api/auth/users/` - Criar novo usuário
- `POST /api/auth/jwt/create/` - Login (retorna access e refresh tokens)
- `POST /api/auth/jwt/refresh/` - Renovar access token
- `GET /api/auth/users/me/` - Informações do usuário logado

### Conhecimentos

- `GET /api/knowledge/` - Listar conhecimentos do usuário
- `GET /api/knowledge/{id}/` - Detalhes de um conhecimento
- `POST /api/knowledge/upload/` - Upload de PDF para processamento
- `PATCH /api/knowledge/{id}/` - Atualizar conhecimento
- `DELETE /api/knowledge/{id}/` - Deletar conhecimento (soft delete)

### Mensagens

- `GET /api/message/` - Listar mensagens do usuário
- `POST /api/message/` - Enviar mensagem e receber resposta do RAG
- `GET /api/message/{id}/` - Detalhes de uma mensagem
- `PATCH /api/message/{id}/` - Atualizar mensagem
- `DELETE /api/message/{id}/` - Deletar mensagem

### Documentação

- `GET /api/schema/` - Schema OpenAPI
- `GET /api/docs/` - Interface Swagger UI

## Fluxo de Uso

1. **Registro/Login**: Crie uma conta ou faça login para obter tokens JWT
2. **Upload de Documento**: Envie um PDF através do endpoint `/api/knowledge/upload/`
3. **Processamento**: O sistema processa o PDF de forma assíncrona:
   - Extrai o texto do documento
   - Gera um título usando GPT
   - Cria embeddings e indexa no ChromaDB
   - Cria o registro de Knowledge
4. **Consulta**: Envie mensagens através do endpoint `/api/message/` para fazer perguntas sobre os documentos enviados
5. **Resposta**: O sistema consulta o ChromaDB, recupera contexto relevante e gera uma resposta usando GPT

## Executando Testes

Para executar os testes da aplicação:

```bash
python manage.py test apps.knowledge.tests
```

Os testes utilizam SQLite em memória automaticamente, não sendo necessário configurar banco de dados adicional.

## Comandos Úteis

### Docker

```bash
# Subir containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### Django

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell do Django
python manage.py shell
```

### Celery

```bash
# Iniciar worker
celery -A config worker --loglevel=info

# Iniciar worker com hot reload
celery -A config worker --loglevel=info --reload

# Ver tarefas em fila
celery -A config inspect active
```

## Notas Importantes

- O arquivo `.env` já está configurado para conectar aos bancos de dados dos containers Docker
- Certifique-se de que os containers estejam rodando antes de iniciar a aplicação Django
- A API key da OpenAI é obrigatória para o funcionamento do sistema de RAG
- Os arquivos PDF enviados são processados de forma assíncrona e podem levar alguns segundos dependendo do tamanho
- O ChromaDB armazena os embeddings dos documentos para busca semântica
