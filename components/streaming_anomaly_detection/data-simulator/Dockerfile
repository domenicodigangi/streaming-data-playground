FROM python:3.11-slim
WORKDIR /app
RUN pip install poetry
COPY . /app
RUN poetry install 
EXPOSE 8001

CMD ["poetry", "run", "simulator"]