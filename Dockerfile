FROM python:3.7

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 9000

COPY ./app /app

VOLUME [ "/app/calques", "/app/audios", "/app/cibles" ]

WORKDIR /app

ARG API_VERSION
ENV API_VERSION ${API_VERSION}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
