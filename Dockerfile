FROM python:3.12.3-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#install nltk related
RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"

# Copy a folder and its contents into the container
COPY processing/ /app/processing/
COPY main.py app.py

EXPOSE 8080
#CMD [ "flask", "run","--host","0.0.0.0","--port","5555"]
# Run with gunicorn (recommended for production)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
#ENTRYPOINT ["python"]
#CMD ["app.py"]
