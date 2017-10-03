FROM heroku/miniconda

RUN conda install scikit-learn numpy scipy

ADD . /opt/webapp

WORKDIR /opt/webapp

RUN pip install -qr requirements.txt

RUN git clone --recursive https://github.com/dmlc/xgboost.git && \
    cd xgboost && \
    make && \
    cd python-package && \
    python setup.py install

CMD gunicorn --bind 0.0.0.0:80 web:app --log-file=-
