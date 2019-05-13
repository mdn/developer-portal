# Use the official Python runtime image as the parent.
FROM python:3.7

EXPOSE 8000
WORKDIR /app/
COPY . /app/

# Install Node.js v12.x.
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# Install Python dependencies.
COPY requirements.txt /app/requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# Install Node.js dependencies.
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
RUN npm ci
RUN npm run build

CMD exec gunicorn developerportal.wsgi:application --bind 0.0.0.0:8000 --workers 3
