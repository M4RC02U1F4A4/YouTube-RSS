FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
USER nobody
EXPOSE 8080
CMD ["gunicorn", "main:app", "-w", "2", "--threads", "4", "-b", "0.0.0.0:8080", "--no-control-socket"]
LABEL org.opencontainers.image.source=https://github.com/M4RC02U1F4A4/YouTube-RSS
