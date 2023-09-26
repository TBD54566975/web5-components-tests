FROM golang:1.21
ADD . /go/web5-test-suite
WORKDIR /go/web5-test-suite
EXPOSE 3000
CMD [ "go", "test", "./test-suite" ]
