FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip

RUN apt-get update && \
    apt-get install -y wget

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Chrome.
RUN apt-get update && apt-get -y install google-chrome-stable

COPY requirements.txt /requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY extract_xlsx.py /extract_xlsx.py

ENTRYPOINT ["python3", "/main.py", "--headless"]
