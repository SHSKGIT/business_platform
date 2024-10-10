FROM python:3.12

MAINTAINER "YUNXIAO WANG"

ENV PYTHONUNBUFFERED=1
# Set environment variables for oracle
ENV ORACLE_HOME=/opt/oracle/instantclient_19_24
ENV PATH=$ORACLE_HOME:$PATH
ENV LD_LIBRARY_PATH=$ORACLE_HOME

RUN mkdir -p /business_platform/webapp/webapp

# Change the working directory to the new directory
WORKDIR /business_platform/webapp/webapp

# copy everything from current directory to work directory
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y libaio1 wget unzip

# Download and install Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/1924000/instantclient-basic-linux.arm64-19.24.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.arm64-19.24.0.0.0dbru.zip -d /opt/oracle && \
    rm instantclient-basic-linux.arm64-19.24.0.0.0dbru.zip

# update pip version. The python interpreter location is up to your computer.
# RUN python -m pip install --upgrade pip

RUN pip install -r ./requirements/base.txt

RUN chmod a+x ./start.sh

RUN apt-get update && apt-get install -y netcat-traditional

# when container starts, execute start.sh
#ENTRYPOINT [ "./start.sh" ]
