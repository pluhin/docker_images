FROM ubuntu:20.04
LABEL maintainer="pluhin@gmail.com"
RUN apt update && apt upgrade \
    && apt install -yqq mc vim curl wget git telnet netcat \    && apt-get purge --auto-remove -yqq \
	&& apt-get clean \
	&& rm -rf \
	    /var/lib/apt/lists/* \
	    /tmp/* \
	    /var/tmp/* \
	    /usr/share/man \
	    /usr/share/doc \
	    /usr/share/doc-base
