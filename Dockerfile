FROM python:3.9-slim-bullseye

ENV VIRTUAL_ENV=C:/Users/aleja/Desktop/envs/dev_sma
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY . /ETL
WORKDIR /ETL
RUN pip install -r requeriments.txt


# Run the application:
COPY etl.py .
CMD ["python3", "etl.py"]