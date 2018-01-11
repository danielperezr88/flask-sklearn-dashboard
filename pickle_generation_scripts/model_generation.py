#!/usr/bin/python
# -*- coding: latin-1 -*-
# Model pickle example: Agro Model

from sklearn.externals import joblib
from os import path

joblib.dump(my_sklearn_model, path.join('..','model','model.pkl'))
