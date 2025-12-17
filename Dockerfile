FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update \
&& apt-get install -y build-essential libpq-dev curl \
&& apt-get clean


COPY requirements.txt /app/
RUN pip install --upgrade pip \
&& pip install -r requirements.txt


COPY . /app/


RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Entrypoint (wait DB, migrate, Gunicorn)
#CMD ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "cinema.wsgi:application"]
