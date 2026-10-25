FROM python:3.12-slim
RUN pip install --no-cache-dir fastapi uvicorn
WORKDIR /srv
COPY main.py .
# exec 형태여야 python이 PID 1로 SIGTERM을 직접 받는다
CMD ["python", "main.py"]