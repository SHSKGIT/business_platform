FROM python:3.12

MAINTAINER "YUNXIAO WANG"

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /business_platform/webapp/webapp

# Change the working directory to the new directory
WORKDIR /business_platform/webapp/webapp

# copy everything from current directory to work directory
COPY . .

# update pip version. The python interpreter location is up to your computer.
# RUN python -m pip install --upgrade pip

RUN pip install -r ./requirements/base.txt

RUN chmod a+x ./start.sh

RUN apt-get update && apt-get install -y netcat-traditional

# when container starts, execute start.sh
#ENTRYPOINT [ "./start.sh" ]
