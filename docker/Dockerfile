# building the python image
FROM python:3

WORKDIR /usr/src/app

#COPY requirements.txt ./
COPY ./ ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./app.py" ]
