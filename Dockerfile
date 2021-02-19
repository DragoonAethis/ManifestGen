FROM ubuntu:20.04

LABEL contact="Julian Szymański, Ryszard Knop, Adrian Siekierka"
LABEL app="ManifestoGen"
LABEL version="1.2"

RUN apt update && apt dist-upgrade -y
RUN apt install -y gnupg2 wget ca-certificates software-properties-common

RUN wget -O- http://download.sgjp.pl/apt/sgjp.gpg.key | apt-key add -
RUN add-apt-repository http://download.sgjp.pl/apt/ubuntu

RUN apt update
RUN apt install -y \
        python3 python3-flask python3-gunicorn gunicorn \
        morfeusz2 python3-morfeusz2 morfeusz2-dictionary-sgjp morfeusz2-dictionary-polimorf

WORKDIR /opt
RUN wget https://github.com/DragoonAethis/ManifestoGen/archive/1.2.tar.gz -O app.tar.gz
RUN wget https://github.com/DragoonAethis/ManifestoGen/releases/download/1.0/plwordnet.sqlite
RUN mkdir /opt/manifestogen
RUN tar xf app.tar.gz -C /opt/manifestogen --strip-components=1
RUN mv plwordnet.sqlite /opt/manifestogen/wordnet
RUN rm /opt/app.tar.gz

EXPOSE 80/tcp
STOPSIGNAL SIGTERM
WORKDIR /opt/manifestogen
CMD gunicorn --workers 2 --bind 0.0.0.0:80 app:app

# Example usage:
# docker build -t dragoonaethis/manifestogen:1.2 .
# docker run --name manifestogen --publish 5000:80/tcp --restart on-failure dragoonaethis/manifestogen:1.2
# Optionally add "-e SCRIPT_NAME=/manifestogen" if you can't pass SCRIPT_NAME via your proxy.

# Example Nginx proxy config:
# location /manifestogen {
#   proxy_pass http://apphostname:5000/manifestogen/;
#   proxy_set_header Host $http_host;
#   proxy_set_header X-Real-IP $remote_addr;
#   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#   proxy_set_header X-Forwarded-Proto $scheme;
#   proxy_set_header SCRIPT_NAME /manifestogen;
# }
