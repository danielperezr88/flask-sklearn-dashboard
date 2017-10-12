#!/usr/bin/python
# -*- coding: latin-1 -*-
# Form generation example: Agro Model

import pickle

with open('../model/form_field.pkl', 'wb') as fp:
    pickle.dump([
            dict(id='Cement',name='Cement',type='number',label='Cement (Kg/m3)',step=.1,value=300.,min=100.,max=550.),
            dict(id='Blast_Furnace_Slag',name='Blast_Furnace_Slag',type='number',label='Blast Furnace Slag (Kg/m3)',step=.1,value=180.,min=0.,max=360.),
            dict(id='Fly_Ash',name='Fly_Ash',type='number',label='Fly Ash (Kg/m3)',step=.1,value=50.,min=0.,max=200.1),
            dict(id='Water',name='Water',type='number',label='Water (Kg/m3)',step=.1,value=180.,min=120.,max=250.),
            dict(id='Superplasticizer',name='Superplasticizer',type='number',label='Superplasticizer (Kg/m3)',step=.1,value=15.,min=0.,max=32.2),
            dict(id='Coarse_Aggregate',name='Coarse_Aggregate',type='number',label='Coarse Aggregate (Kg/m3)',step=.1,value=850.,min=801.,max=1145.),
            dict(id='Fine_Aggregate',name='Fine_Aggregate',type='number',label='Fine Aggregate (Kg/m3)',step=.1,value=850.,min=594.,max=993.),
            dict(id='Age',name='Age',type='number',label='Age (days)',step=.1,value=0,min=1,max=365),
            # Put OneHot encoded fields (comma separated) like this
            # dict(type='text',name='onehot',value='WildArea,SoilType',hidden=True),
            # Put Randomizable fields (comma separated) like this. Please, make sure to give correct min/max values to each one before.
            dict(type='text',name='random',value='Cement,Blast_Furnace_Slag,Fly_Ash,Water,Superplasticizer,Coarse_Aggregate,Fine_Aggregate,Age',hidden=True)
        ],
        fp
    )