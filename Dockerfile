# Use the official Python runtime image as the parent.
FROM python:3.7

EXPOSE 8000
WORKDIR /app/

# Environment variables.
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev

# Install Node.js v12.x.
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# Install Python dependencies.
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Install Node.js dependencies.
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
RUN npm ci

# Copy the project into /app directory.
COPY . /app/

# Run migrations.
RUN python manage.py migrate

RUN npm run build

CMD exec gunicorn developerportal.wsgi:application --bind 0.0.0.0:8000 --workers 3
