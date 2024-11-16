FROM python
WORKDIR /app
COPY . .
RUN pip install -r requirements/prod.txt
RUN cd zenbill
EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
