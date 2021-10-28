## docker build -t nexus.prjx.uk/repository/main/labmgt .
## docker tag 1f04cebf1007 nexus.prjx.uk/repository/main/labmgt:v0.1
## docker push nexus.prjx.uk/repository/main/labmgt
## docker docker pull nexus.prjx.uk/repository/main/labmgt:latest

## docker build -t nexus.prjx.uk/repository/main/labmgt:v0.1.1-amd64 --build-arg ARCH=amd64/ .
## docker tag 1f04cebf1007 nexus.prjx.uk/repository/main/labmgt:v0.1.1-amd64
## docker push nexus.prjx.uk/repository/main/labmgt
## docker docker pull nexus.prjx.uk/repository/main/labmgt:v0.1.1-amd64

ARG ARCH=
FROM dp.prjx.uk/${ARCH}python:3.10-alpine
ADD . /app
RUN apk add git && pip install -r /app/requirements.txt
CMD ["echo", "You need to pass the command to run!"]