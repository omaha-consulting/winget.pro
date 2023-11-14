FROM python:3.9

ENV DEBUG=False
ENV HOST_NAME=*
# Keep the DB file in a separate directory, which can be shared as a volume.
ENV SQLITE_DB_FILE=/srv/db/db.sqlite3

WORKDIR /srv

COPY . .

RUN mkdir `dirname $SQLITE_DB_FILE`

RUN pip install --no-cache-dir -Ur requirements/base-full.txt

RUN python manage.py collectstatic --noinput

EXPOSE 8000

RUN chmod +x /srv/deploy/docker/start.sh

CMD ["/srv/deploy/docker/start.sh"]