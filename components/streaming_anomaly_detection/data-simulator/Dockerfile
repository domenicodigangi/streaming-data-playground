FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install poetry

RUN poetry install 

EXPOSE 8000

CMD ["poetry", "run", "simulator"]