# Pede Aí

Sistema de gerenciamento de pedidos com arquitetura baseada em mensageria usando RabbitMQ.

# Integrantes:
* Mário Bernardo Balen (1136196)
* Pablo Henrique Strücker Sarturi (1136331)

## O que é

O Pede Aí é uma aplicação que conecta clientes e restaurantes através de um sistema robusto de processamento de pedidos. Utiliza filas de mensagens para garantir comunicação assíncrona entre componentes, com tratamento de erros e atualização de status em tempo real.

## Arquitetura

```
Frontend (Angular) -> API Django -> RabbitMQ -> Consumidores -> Banco de Dados
```

## Componentes

### Backend
- **API Django**: Gerencia pedidos e restaurantes via REST
- **Message Broker**: RabbitMQ para comunicação assíncrona
- **Consumidores**: Processam mensagens e atualizam banco de dados
- **Dead Letter Queue**: Trata mensagens com falha

### Frontend
- **Listagem de Restaurantes**: Exibe restaurantes disponíveis
- **Detalhes do Restaurante**: Visualiza menu e produtos
- **Carrinho e Checkout**: Cria novos pedidos
- **Rastreamento**: Acompanha status dos pedidos em tempo real
- **Dashboard**: Painel para restaurantes gerenciarem pedidos

## Pré-requisitos

- Python 3.8+
- Node.js 18+
- Docker e Docker Compose

## Como Executar (Dev)

### 1. Clonar o Repositório
```bash
git clone <seu-repositorio>
cd pede-ai
```

### 2. Iniciar RabbitMQ
```bash
cd backend/broker
docker-compose up -d
```

### 3. Configurar Backend
```bash
# Criar ambiente virtual
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Instalar dependências
cd backend/server
pip install -r requirements.txt

# Criar infraestrutura de filas
cd backend/broker
python setup.py

# Aplicar migrações
cd backend/server
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### 4. Iniciar Consumidores
```bash
# Terminal separado (com venv ativado)
cd backend/broker
python client_consumer.py

# Outro terminal para consumidor de status
python restaurant_consumer.py
```

### 5. Configurar Frontend
```bash
cd frontend
npm install
npm start
```

## Acessar a Aplicação

- Frontend: http://localhost:4200
- API: http://localhost:8000
- RabbitMQ Console: http://localhost:15672 (admin/admin123)

## Estrutura de Filas

| Fila | Propósito |
|------|-----------|
| `new_orders` | Novos pedidos criados |
| `status_updates` | Atualizações de status |
| `order_delivered` | Confirmação de entrega |
| `dead_orders` | Mensagens com erro |

## Ferramentas

- **Backend**: Python, Django, Django REST Framework
- **Frontend**: Angular, TypeScript, SCSS
- **Mensageria**: RabbitMQ, Pika
- **Infraestrutura**: Docker, Docker Compose
- **Banco de Dados**: Django ORM (SQLite por padrão)
