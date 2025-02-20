
FROM python:3.10

RUN useradd -m zapuser
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN chown -R zapuser:zapuser /app
USER zapuser

EXPOSE 5050

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "app:app"]