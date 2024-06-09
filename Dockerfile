FROM python:3.12.3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./config.yml /code/config.yml
COPY ./src /code/src/
COPY ./images/arXiv.png /code/images/arXiv.png

EXPOSE 8080



CMD ["streamlit", "run", "src/app.py"]