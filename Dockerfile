FROM python:2.7

# Update the software package list and do necessary upgrades
RUN apt-get update --fix-missing || exit 0
RUN apt-get upgrade -y
RUN apt-get install vim curl wget -y

WORKDIR /app
COPY techtrends/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy app code
COPY techtrends/ .

# Initialize DB
RUN python init_db.py

EXPOSE 3111
CMD ["python", "app.py"]