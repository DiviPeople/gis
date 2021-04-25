FROM ubuntu:20.04
MAINTAINER Dmitry Ivanko <tmwsls12@gmail.com>

ENV HOME /var/www

ENV TERM xterm

RUN sed -i 's/^# deb-src /deb-src /' /etc/apt/sources.list \
 && apt-get update \
 && mkdir /var/www \
 && cd /var/www \
 && apt-get install -y libncurses5-dev libncursesw5-dev dpkg-dev build-essential gcc-arm-linux-gnueabihf flex bison \
 && apt-get source -y linux

WORKDIR "${HOME}"

COPY docker-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
