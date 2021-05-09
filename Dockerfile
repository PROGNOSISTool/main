FROM ubuntu
RUN apt-get update && apt-get -y install curl wget git cloc
COPY . /code
WORKDIR /code
RUN chmod +x ./analysis.sh
CMD ./analysis.sh
