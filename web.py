#!/usr/bin/python
# -*- coding: latin-1 -*-
from flask import Flask, render_template, redirect, url_for, g, abort, session, request, flash, send_from_directory
import werkzeug.exceptions as ex

import requests as req
from hashlib import sha512
from binascii import hexlify

from os import path, getpid, urandom, makedirs
import inspect

import logging

from utils import refresh_and_retrieve_module, BucketedFileRefresher

from sklearn.externals import joblib
import pandas as pd
import pickle

__author__ = "Daniel Pérez"
__email__ = "dperez@human-forecast.com"


def refresh_and_retrieve_pickle(filename, bucket=None, subfolder=None, use_joblib=False):

    try:

        to_join = [path.dirname(path.realpath(__file__))]
        to_join += [subfolder] if subfolder is not None else []
        to_join += [filename]

        filepath = path.join(*to_join)

        if bucket is not None:
            BFR(bucket, filename, filepath)

        with open(filepath, 'rb') as fp:
            if use_joblib:
                return joblib.load(fp)
            return pickle.load(fp)

    except BaseException as ex:

        msg = "Unable to access file \"%s\": Unreachable or unexistent bucket and file." % (filename,)
        logging.error(msg)
        raise ImportError(msg)

    except FileNotFoundError as e:

        msg = "Unable to access file \"%s\": Unreachable or unexistent bucket and file." % (filename,)
        logging.error(msg)
        raise ImportError(msg)


def no_impostors_wanted(s):
    if (not s['logged_in']) if 'logged_in' in s.keys() else True:
        abort(403)


def save_pid():
    """Save pid into a file: filename.pid."""
    pidfilename = inspect.getfile(inspect.currentframe()) + ".pid"
    f = open(pidfilename, 'w')
    f.write(str(getpid()))
    f.close()


def generate_url(host, protocol='http', port=80, directory=''):

    if isinstance(directory, list):
        directory = '/'.join(directory)

    return "%s://%s:%d/%s" % (protocol, host, port, directory)


def run():
    flask_options = dict(port=PORT, host='0.0.0.0')
    app.secret_key = hexlify(urandom(24))#hexlify(bytes('development_', encoding='latin-1'))
    app.run(**flask_options)

# Flask Web server
app = Flask(__name__, static_folder='browser/static', template_folder='browser/templates')
app.config['model_folder'] = 'model'

MY_IP = req.get(generate_url('jsonip.com')).json()['ip']
PORT = 88

ID_BUCKET = 'ids'
MODEL_BUCKET = 'scikit-learn-models'

BFR = BucketedFileRefresher()

model_folder = 'model'
if not path.exists(model_folder):
    makedirs(model_folder)


@app.route('/model/<path:filename>')
def model(filename):
    return send_from_directory(app.config['model_folder'], filename)


@app.route('/', methods=['GET'])
def root():
    if (not session['logged_in']) if 'logged_in' in session.keys() else True:
        return redirect('/login')
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if (not session['logged_in']) if 'logged_in' in session.keys() else True:
        return redirect('/login')

    mdl = refresh_and_retrieve_pickle('model.pkl', bucket=MODEL_BUCKET, subfolder=model_folder, use_joblib=True)
    cls_info = refresh_and_retrieve_pickle('classes_info.pkl', bucket=MODEL_BUCKET, subfolder=model_folder)
    inputs = refresh_and_retrieve_pickle('form_field.pkl', bucket=MODEL_BUCKET, subfolder=model_folder)

    for im in cls_info['images'].values():
        BFR(MODEL_BUCKET, im, path.join(model_folder, im))

    ipt_rnd = [i for i in inputs if i['name'] == 'random']
    if len(ipt_rnd) > 0:
        to_rndmize = ipt_rnd[0]['value'].split(',')
        for n in range(len(inputs)):
            if inputs[n]['name'] in to_rndmize:
                istep = inputs[n]['step'] if 'step' in inputs[n] else 1
                imin = inputs[n]['min'] if 'min' in inputs[n] else 0
                imax = inputs[n]['max'] if 'max' in inputs[n] else 254
                inputs[n]['value'] = int(pd.np.random.uniform(imin, imax + istep)/istep) * istep

    df = None
    if len(request.form) > 0:
        df = pd.DataFrame(dict(request.form))

        for c in [c for c in df.columns if c not in ['onehot', 'random']]:
            if df[c].dtype == 'object':
                df[c] = int(df[c].as_matrix()[0])

        if 'random' in df.columns:
            df.drop(['random'], axis=1, inplace=True)

        if 'onehot' in df.columns:
            onehot_encoded = df['onehot'][0].split(',')
            for field in onehot_encoded:
                vopts = [i for i in inputs if (i['id'] == field if 'id' in i else False)][0]['options']
                vopts = [o['value'] for o in vopts]
                vmin, vmax = min(vopts), max(vopts)
                for n in range(vmax-vmin + 1):
                    df[field+str(n)] = pd.np.any(df[field] == n)

                df.drop([field], axis=1, inplace=True)
            df.drop(['onehot'], axis=1, inplace=True)

    result = mdl.predict(df) if (mdl is not None and df is not None) else None
    result_name = (cls_info['names'][result[0]] if result[0] in cls_info else cls_info['names'][str(result[0])]) \
        if result is not None else None
    result_img = (cls_info['images'][result[0]] if result[0] in cls_info else cls_info['images'][str(result[0])]) \
        if result is not None else None
    result_descr = (cls_info['descriptions'][result[0]] if result[0] in cls_info
                    else cls_info['descriptions'][str(result[0])]) \
        if result is not None else None

    return render_template('index.html',
                           headerized_class="non-headerized",
                           inputs=inputs,
                           result_name=result_name,
                           result_img=result_img,
                           result_descr=result_descr
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():

    ids = refresh_and_retrieve_module('id_digests.py', ID_BUCKET).id_dict

    if request.method == 'POST':
        uname = request.form['username']
        if uname in ids.keys():
            pwd = request.form['password']
            pwd = pwd.encode('latin1')
            digest = sha512(pwd).hexdigest()
            if ids[uname] == digest:
                session['username'] = request.form['username']
                session['logged_in'] = True
                return redirect(url_for('index'))
            flash('Password did not match that for the login provided', 'bad_login')
            return render_template('login.html', headerized_class="non-headerized")
        flash('Unknown username', 'bad_login')
    return render_template('login.html', headerized_class="non-headerized")


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', headerized_class="non-headerized")


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return 'beating', 200


@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.errorhandler(401)
def void_or_nonexistent_term(e):
    return render_template('401.html'), 401


@app.errorhandler(403)
def void_or_nonexistent_term(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def void_or_nonexistent_term(e):
    return render_template('404.html'), 404


if __name__ == '__main__':

    save_pid()

    dirname = path.dirname(path.realpath(__file__))
    logfilename = inspect.getfile(inspect.currentframe()) + ".log"
    logging.basicConfig(filename=logfilename, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("Started")

    run()
