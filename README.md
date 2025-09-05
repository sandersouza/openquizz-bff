# OpenQuiz BFF

Backend para o projeto OpenQuiz, um clone estilo Kahoot com arquitetura **Backend for Frontend** usando FastAPI.

## Rodando o projeto

```bash
docker compose up --build
```

Isso inicia os serviços com Traefik, MongoDB e Redis. O BFF Admin fica exposto em `http://localhost/admin`.

## Health check

```bash
curl http://localhost/admin/healthz
```

## Exemplo de uso da API

### Criar quiz

```bash
curl -X POST http://localhost/admin/quizzes \
  -H 'Content-Type: application/json' \
  -d '{"title":"Meu Quiz","questions":[]}'
```

### Listar quizzes

```bash
curl http://localhost/admin/quizzes
```

### Buscar quiz por id

```bash
curl http://localhost/admin/quizzes/ID_DO_QUIZ
```

### Atualizar quiz

```bash
curl -X PUT http://localhost/admin/quizzes/ID_DO_QUIZ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Quiz Atualizado","questions":[]}'
```

### Excluir quiz

```bash
curl -X DELETE http://localhost/admin/quizzes/ID_DO_QUIZ
```

## Postman

Uma collection Postman com esses endpoints está disponível em [OpenQuiz.postman_collection.json](./OpenQuiz.postman_collection.json).

