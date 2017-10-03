FROM danielperezr88/python3

RUN apt-get update && apt-get install -y \
        python-dev \
        git

RUN curl -SL 'https://bootstrap.pypa.io/get-pip.py' | python2 \
	&& pip2 install --no-cache-dir --upgrade pip==$PYTHON_PIP_VERSION \
	&& cd / \
	&& curl -fSL "https://gist.githubusercontent.com/danielperezr88/c3b7eb74c30d854f6db4b978a2f34582/raw/416a99ebddf210cf6f44173e79faeef98bfeb15d/pip_shebang_patch.txt" \
			-o /pip_shebang_patch.txt \
	&& patch -p1 < pip_shebang_patch.txt

RUN pip2 install --upgrade numpy && \
    pip2 install --upgrade scipy

RUN pip install --upgrade pip && \
	pip install redis && \
	pip install gunicorn

RUN git clone --recursive https://github.com/dmlc/xgboost.git && \
    cd xgboost && \
    make && \
    cd python-package && \
    python setup.py install && \
    python2 setup.py install

RUN mkdir /app

RUN git clone https://github.com/danielperezr88/flask-sklearn-dashboard.git /app

WORKDIR /app

RUN git checkout concrete

EXPOSE 88

CMD ["gunicorn -b 0.0.0.0:80 web:app"]
