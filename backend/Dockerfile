FROM python:3.10-slim
WORKDIR /app
COPY /requirements.txt .
# RUN pip3 install -r ./requirements.txt --no-cache-dir
RUN pip3 install --upgrade pip && pip3 install -r ./requirements.txt --no-cache-dir
COPY . .
RUN python recipe_app/manage.py collectstatic --noinput
CMD ["gunicorn", "recipe_app.wsgi:application", "--bind", "0:8000" ]