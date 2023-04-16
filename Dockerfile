FROM python:3.11-slim
RUN mkdir app
COPY app /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["./starter.sh"]
# CMD [ "python", "./server.py"]