FROM danielperezr88/python3

RUN apt-get update && apt-get install -y \
        python-dev \
        supervisor \
        git

RUN curl -SL 'https://bootstrap.pypa.io/get-pip.py' | python2 \
	&& pip2 install --no-cache-dir --upgrade pip==$PYTHON_PIP_VERSION \
	&& cd / \
	&& curl -fSL "https://gist.githubusercontent.com/danielperezr88/c3b7eb74c30d854f6db4b978a2f34582/raw/416a99ebddf210cf6f44173e79faeef98bfeb15d/pip_shebang_patch.txt" \
			-o /pip_shebang_patch.txt \
	&& patch -p1 < pip_shebang_patch.txt

RUN pip2 install supervisor && \
    pip2 install superlance==1.0.0

RUN pip install --upgrade pip && \
	pip install redis

RUN mkdir -p /var/log/supervisor
RUN mkdir /app

RUN git clone https://github.com/danielperezr88/flask-sklearn-dashboard.git /app

WORKDIR /app

RUN git checkout agro && \
	mv supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["/usr/bin/supervisord"]
