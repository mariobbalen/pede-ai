FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/server/ .
COPY backend/broker/setup.py backend/broker/config.py ./broker/

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["runserver"]
