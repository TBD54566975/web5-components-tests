FROM golang:1.20.2-alpine

RUN apk add --no-cache git

WORKDIR /app

RUN git clone https://github.com/TBD54566975/ssi-service.git

WORKDIR /app/ssi-service

RUN go mod download
RUN go build -tags jwx_es256k -o /docker-ssi-service ./cmd/ssiservice
RUN rm config/config.toml
RUN cp config/compose.toml config/config.toml

EXPOSE 3000

CMD [ "/docker-ssi-service" ]
