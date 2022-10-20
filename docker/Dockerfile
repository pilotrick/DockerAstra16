ARG  ODOO_VERSION
FROM odoo:${ODOO_VERSION:-16.0}

# change to the root user
USER root

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install git python3 python3-pip build-essential wget python3-dev python3-venv python3-wheel libxslt1-dev -y
RUN apt-get install libzip-dev libldap2-dev libsasl2-dev python3-setuptools node-less gdebi -y
RUN pip3 install pip --upgrade
#RUN apt-get -y update && pip3 install ptvsd
#RUN cp /usr/bin/odoo /usr/bin/odoo-bin
#COPY odoo-bin /usr/bin/odoo
#RUN chmod -R 777 /usr/bin/odoo

COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt

RUN apt-get update
RUN apt-get install -y curl nano ssh nano

# change to the odoo user

EXPOSE 5678
USER odoo
