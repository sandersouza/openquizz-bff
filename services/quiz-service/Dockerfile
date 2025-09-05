FROM python:3.12-slim
WORKDIR /app
COPY packages /packages
COPY services/quiz-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e /packages/common_schemas
COPY services/quiz-service/app /app/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
