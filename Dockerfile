FROM node:18.12.1-bullseye-slim AS frontend

WORKDIR /frontend

COPY server/frontend/package*.json ./
RUN npm install

COPY server/frontend/ ./
RUN npm run build

FROM python:3.12.0-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP=/app

WORKDIR $APP

COPY server/requirements.txt $APP/requirements.txt
RUN pip3 install -r requirements.txt

COPY server/ $APP
COPY --from=frontend /frontend/build $APP/frontend/build

EXPOSE 8000

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 djangoproj.wsgi"]
