#!/usr/bin/env bash
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but not found on PATH." >&2
  echo "Install Node.js/npm first, then retry." >&2
  exit 1
fi

export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PWCLI="${PWCLI:-$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh}"

if [[ ! -x "$PWCLI" ]]; then
  echo "Error: Playwright wrapper not found or not executable at: $PWCLI" >&2
  exit 1
fi

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="${SESSION:-openquiz-create-quiz}"
OUTPUT_DIR="${OUTPUT_DIR:-output/playwright/create-quiz}"
HEADED="${HEADED:-true}"

QUIZ_TITLE="${QUIZ_TITLE:-Playwright Quiz $(date +%Y%m%d-%H%M%S)}"
QUESTION_TEXT="${QUESTION_TEXT:-What is 2 + 2?}"
ANSWER_1="${ANSWER_1:-4}"
ANSWER_2="${ANSWER_2:-5}"
TIME_LIMIT="${TIME_LIMIT:-20}"

OPEN_FLAGS=()
if [[ "$HEADED" == "true" ]]; then
  OPEN_FLAGS+=(--headed)
fi

mkdir -p "$OUTPUT_DIR"

AUTOMATION_CODE=$(cat <<'JS'
const timeout = 15000;

async function fillInput(selector, value) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
  await page.locator(selector).fill(value);
}

await fillInput('input[placeholder="Title"]', process.env.QUIZ_TITLE || 'Playwright Quiz');
await fillInput('input[placeholder="Question"]', process.env.QUESTION_TEXT || 'What is 2 + 2?');
await fillInput('input[placeholder="Answer"] >> nth=0', process.env.ANSWER_1 || '4');
await fillInput('input[placeholder="Answer"] >> nth=1', process.env.ANSWER_2 || '5');
await fillInput('input[type="number"]', String(process.env.TIME_LIMIT || '20'));

await page.getByRole('button', { name: 'New Quiz' }).click();
await page.waitForURL(/\/quizzes$/, { timeout });
await page.waitForSelector('table tbody tr', { timeout });
JS
)

(
  cd "$OUTPUT_DIR"
  cleanup() {
    "$PWCLI" --session "$SESSION" close >/dev/null 2>&1 || true
  }
  trap cleanup EXIT

  QUIZ_TITLE="$QUIZ_TITLE" \
  QUESTION_TEXT="$QUESTION_TEXT" \
  ANSWER_1="$ANSWER_1" \
  ANSWER_2="$ANSWER_2" \
  TIME_LIMIT="$TIME_LIMIT" \
  "$PWCLI" --session "$SESSION" open "$BASE_URL/quizzes/new" "${OPEN_FLAGS[@]}"

  QUIZ_TITLE="$QUIZ_TITLE" \
  QUESTION_TEXT="$QUESTION_TEXT" \
  ANSWER_1="$ANSWER_1" \
  ANSWER_2="$ANSWER_2" \
  TIME_LIMIT="$TIME_LIMIT" \
  "$PWCLI" --session "$SESSION" run-code "$AUTOMATION_CODE"

  "$PWCLI" --session "$SESSION" snapshot > final_snapshot.txt
  "$PWCLI" --session "$SESSION" screenshot
)

echo "Workflow completed. Artifacts saved in: $OUTPUT_DIR"
