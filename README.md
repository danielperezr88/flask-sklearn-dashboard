Flask's scikit-learn web-based dashboard
========================================
Flask rapid prototyping framework for one-page scientific Heroku-ready webapps. It relies on joblib's model
dump capacity and given a set of field names, data-types and some other optional data, constructs a simple
AJAX form for querying the model with user data.

::

  SCOPE:     [New Product Development]
  TARGET:    [Rapid Prototyping]
  STATUS:    [Production Ready]

  
Tested with
-----------
* Python 3.4

Dependencies
------------
* Flask
* scikit-learn
* Pandas
* requests
* redis
 
 Way of use (examples in "pickle_generation_scripts" folder)
 -----------------------------------------------------------
 * Put the following files into "model" folder:
    - __model.pkl__ - pickle file for our scikit-learn model, generated with joblib's "dump" function.
    - __classes_info.pkl__ - pickle file for result visualization configuration, with the following structure:
    
    
            {
                names:{
                    'class 1 id': 'class 1 name',
                    'class 2 id': 'class 2 name',
                    ...
                    'class n id': 'class n name'
                },
                images:{
                    'class 1 id': 'class 1 image',
                    'class 2 id': 'class 2 image',
                    ...
                    'class n id': 'class n image'
                },
                descriptions:{
                    'class 1 id': 'class 1 description',
                    'class 2 id': 'class 2 description',
                    ...
                    'class n id': 'class n description'        
                }
            }
   - __form_fields.pkl__ - pickle for form fields configuration, with the following structure:
            
            [
                {'id':'a_field_input','name':'c','type':'text','label':'A Field','placeholder':'Write some text here...'},
                {'id':'b_field_input','name':'c','type':'number','label':'B Field','value':.5,'min':0.,'max':.9,'step':0.1},
                {'id':'c_field_input','name':'c','type':'select','label':'C Field','options':[
                    {'value':'x','name':'X Value'},
                    {'value':'y','name':'Y Value',selected=True},
                    {'value':'z','name':'Z Value'}
                ]}
                ...
            ]

Notes:
------
This project is Heroku-ready by Docker containerization, and supports xgboost-based scikit-learn models.
