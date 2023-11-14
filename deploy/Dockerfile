FROM python:3.9

ENV DEBUG=False
ENV HOST_NAME=*

WORKDIR /srv

COPY . .

RUN pip install --no-cache-dir -Ur requirements/base-full.txt

RUN python manage.py migrate

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--log-level=warning", "--log-file=-"]