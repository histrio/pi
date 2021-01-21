FROM alpine:latest

RUN apk --no-cache add curl git bash openssh procps
ADD https://raw.githubusercontent.com/simonthum/git-sync/master/git-sync /usr/bin/git-sync
RUN chmod +x /usr/bin/git-sync

WORKDIR /git
ENV TERM=xterm

ENTRYPOINT bash -c 'while sleep $(echo 120-`date "+%s"`%120 | bc); do /usr/bin/git-sync -n; done'

