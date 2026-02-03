# Playwright workflow automation

## Prerequisites

```bash
command -v npx >/dev/null 2>&1
```

## Run

```bash
./scripts/playwright/create_quiz_workflow.sh
```

## Optional env vars

```bash
BASE_URL=http://localhost:3000 \
SESSION=openquiz-create-quiz \
HEADED=true \
QUIZ_TITLE="My Quiz" \
QUESTION_TEXT="Capital of Brazil?" \
ANSWER_1="Brasilia" \
ANSWER_2="Rio" \
TIME_LIMIT=20 \
OUTPUT_DIR=output/playwright/create-quiz \
./scripts/playwright/create_quiz_workflow.sh
```

Artifacts are written to `output/playwright/create-quiz/`.
