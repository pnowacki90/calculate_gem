FROM python:alpine
WORKDIR /usr/local/app
RUN mkdir /usr/local/files && touch /usr/local/files/gem.log && chmod 777 /usr/local/files/gem.log

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY gem_script.py ./
COPY config.py ./
COPY connect.py ./

RUN addgroup -S app && adduser -S app -G app
USER app

CMD ["python3", "gem_script.py"]
