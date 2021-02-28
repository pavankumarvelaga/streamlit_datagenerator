FROM python:3.8

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app/

EXPOSE 8080
CMD streamlit run --server.port 8080 --server.enableCORS false --server.enableXsrfProtection false app/server.py