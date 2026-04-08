FROM python:3.11-slim

WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "core.wsgi:application"]


#from yt example
#FROM python:3.11-slim

#WORKDIR /app

#COPY pyproject.toml uv.lock ./

#RUN pip install uv && uv sync --frozen

#COPY . .

#EXPOSE 8000