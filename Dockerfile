FROM python:3.7

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"

ADD requirements.txt /myworkdir/requirements.txt 
ADD ./dashboard /myworkdir/dashboard
ADD ./data/df_mdb_wp.csv /myworkdir/data/df_mdb_wp.csv
ADD ./data/df_mdb.csv /myworkdir/data/df_mdb.csv

WORKDIR /myworkdir

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 
EXPOSE 8050

# Run the application:
CMD ["python3", "./dashboard/abgeordneten-dashboard.py"]