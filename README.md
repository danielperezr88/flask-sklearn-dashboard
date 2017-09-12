Flask's scikit-learn web-based dashboard
========================================

Testado en las siguientes versiones de python
---------------------------------------------
* Python 3.4

Dependencias
------------
* Flask
* scikit-learn
* Pandas
* requests
* redis
 
 Modo de uso
 -----------
 * Introducir en la carpeta "model", los archivos:
    - __model.pkl__ - pickle del modelo de scikit-learn a evaluar, generado con la función "dump" de joblib)
    - __classes_info.pkl__ - pickle para la visualización de los resultados con la siguiente estructura:
    
    
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
   - __form_fields.pkl__ - pickle para la construcción del formulario con la siguiente estructura:
            
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
   