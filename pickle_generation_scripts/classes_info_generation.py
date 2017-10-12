#!/usr/bin/python
# -*- coding: latin-1 -*-
# Classes info example: Agro Model

import pickle
import numpy as np

# All fields are mandatory
with open('../model/classes_info.pkl', 'wb') as fp:
    pickle.dump(dict(
            is_regressor=True,
            in_dtypes=[np.float32,np.float32,np.float32,np.float32,np.float32,np.float32,np.float32,np.float32],
            out_dtype=[np.float32],
            result_text="Optimal Compression force is %s (MPa)"
        ),
        fp
    )