FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY skilljar_gen_code2.py ./

CMD [ "python", "./skilljar_gen_code2.py"]
