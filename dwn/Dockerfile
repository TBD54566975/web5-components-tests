FROM node:18-alpine3.15

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

WORKDIR /dwn

# TODO: Change to main when test/dnw-steelthread-test is merged
RUN git clone -b test/dnw-steelthread-test https://github.com/TBD54566975/dwn-relay.git

WORKDIR /dwn/dwn-relay

# We want a fresh run every time so we delete persisted data if it exists
RUN rm -Rf ./BLOCKSTORE

RUN mkdir -p etc
RUN cp ./example/config.js etc/


# DWN's levelDB has issues running on m1, so we have to install prerequisites and build from source
RUN apk add --update python3 make g++
RUN npm install --build-from-source

EXPOSE 9000

CMD node --es-module-specifier-resolution=node src