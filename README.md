# OpenQuiz BFF

Backend para o projeto OpenQuiz, um clone estilo Kahoot com arquitetura **Backend for Frontend** usando FastAPI.

## Rodando o projeto

```bash
docker compose up --build
```

Isso inicia os serviços com Traefik, MongoDB e Redis.

## OpenAPI

Cada serviço expõe documentação automática:

- `http://localhost/admin/docs` — Admin BFF (Swagger UI)
- `http://localhost/player/docs` — Player BFF
- `http://localhost/ws/docs` — Gateway WebSocket

## Endpoints

### Admin (`/admin`)

#### Health

```bash
curl http://localhost/healthz
curl http://localhost/admin/healthz
```

#### Quizzes

```bash
# Criar quiz
curl -X POST http://localhost/admin/quizzes \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Meu Quiz",
    "questions": [{
      "id": "q1",
      "text": "Capital do Brasil?",
      "options": ["Rio", "Brasília", "São Paulo"],
      "correct": [1]
    }]
  }'

# Listar quizzes
curl http://localhost/admin/quizzes

# Buscar quiz
curl http://localhost/admin/quizzes/ID_DO_QUIZ

# Atualizar quiz
curl -X PUT http://localhost/admin/quizzes/ID_DO_QUIZ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Quiz Atualizado","questions":[]}'

# Excluir quiz
curl -X DELETE http://localhost/admin/quizzes/ID_DO_QUIZ
```

#### Sessions

```bash
# Criar sessão
curl -X POST http://localhost/admin/sessions \
  -H 'Content-Type: application/json' \
  -d '{"quiz_id":"ID_DO_QUIZ"}'

# Iniciar sessão
curl -X POST http://localhost/admin/sessions/ID_DA_SESSAO/start

# Próxima pergunta
curl -X POST http://localhost/admin/sessions/ID_DA_SESSAO/next

# Encerrar sessão
curl -X POST http://localhost/admin/sessions/ID_DA_SESSAO/end

# Buscar sessão
curl http://localhost/admin/sessions/ID_DA_SESSAO
```

### Player (`/player`)

```bash
# Health
curl http://localhost/player/healthz

# Entrar em sessão
curl -X POST http://localhost/player/join \
  -H 'Content-Type: application/json' \
  -d '{"pin":"123456","nickname":"Jogador"}'
```

### WebSocket (`/ws/{session_id}`)

```bash
websocat ws://localhost/ws/ID_DA_SESSAO
```

Eventos publicados no Redis no canal `room:{session_id}` são retransmitidos para todos os clientes conectados nesse endpoint.

## Postman

Uma collection Postman com esses endpoints está disponível em [OpenQuiz.postman_collection.json](./OpenQuiz.postman_collection.json).

