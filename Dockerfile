FROM python:slim-buster
RUN apt-get update && apt-get upgrade -y

WORKDIR /code
COPY ./Pipfile.lock /code
COPY ./Pipfile /code
RUN pip3 install pipenv; \
    pipenv install --system --deploy
COPY . /code/

# Compile to pyc for faster startup
RUN python -m compileall .

ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]
