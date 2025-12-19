FROM python:3.11-slim

WORKDIR /app

COPY main.py .

RUN pip install fastapi uvicorn psycopg2-binary

EXPOSE 8000

CMD ["python", "main.py"]
