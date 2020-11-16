FROM debian:sid-20201012

RUN apt-get update && \
    apt-get install -y gitit && mkdir /gitit

WORKDIR /gitit
COPY default.conf default.conf
ENTRYPOINT ["gitit", "-f", "default.conf"]
