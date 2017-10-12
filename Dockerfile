FROM heroku/miniconda:3

RUN apt-get update && apt-get install -y \
        python-dev \
        build-essential

RUN conda install numpy scipy scikit-learn==0.18.1

RUN git clone --recursive https://github.com/dmlc/xgboost.git && \
    cd xgboost && \
    make && \
    cd python-package && \
    python setup.py install

ADD . /opt/webapp

WORKDIR /opt/webapp

RUN pip install -qr requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT web:app --log-file=-
