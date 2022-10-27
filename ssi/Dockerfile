FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install golang-go

WORKDIR /app

RUN git clone https://github.com/TBD54566975/ssi-service.git

WORKDIR /app/ssi-service

RUN ls -alt
RUN go mod download
RUN go build -tags jwx_es256k -o /docker-ssi-service ./cmd

EXPOSE 3000

CMD [ "/docker-ssi-service" ]


