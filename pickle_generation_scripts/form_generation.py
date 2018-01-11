#!/usr/bin/python
# -*- coding: latin-1 -*-
# Form generation example: Agro Model

import pickle

soiltypes = {
    "1": "Cathedral family - Rock outcrop complex, extremely stony.",
    "2": "Vanet - Ratake families complex, very stony.",
    "3": "Haploborolis - Rock outcrop complex, rubbly.",
    "4": "Ratake family - Rock outcrop complex, rubbly.",
    "5": "Vanet family - Rock outcrop complex complex, rubbly.",
    "6": "Vanet - Wetmore families - Rock outcrop complex, stony.",
    "7": "Gothic family.",
    "8": "Supervisor - Limber families complex.",
    "9": "Troutville family, very stony.",
    "10": "Bullwark - Catamount families - Rock outcrop complex, rubbly.",
    "11": "Bullwark - Catamount families - Rock land complex, rubbly.",
    "12": "Legault family - Rock land complex, stony.",
    "13": "Catamount family - Rock land - Bullwark family complex, rubbly.",
    "14": "Pachic Argiborolis - Aquolis complex.",
    "15": "unspecified in the USFS Soil and ELU Survey.",
    "16": "Cryaquolis - Cryoborolis complex.",
    "17": "Gateview family - Cryaquolis complex.",
    "18": "Rogert family, very stony.",
    "19": "Typic Cryaquolis - Borohemists complex.",
    "20": "Typic Cryaquepts - Typic Cryaquolls complex.",
    "21": "Typic Cryaquolls - Leighcan family, till substratum complex.",
    "22": "Leighcan family, till substratum, extremely bouldery.",
    "23": "Leighcan family, till substratum - Typic Cryaquolls complex.",
    "24": "Leighcan family, extremely stony.",
    "25": "Leighcan family, warm, extremely stony.",
    "26": "Granile - Catamount families complex, very stony.",
    "27": "Leighcan family, warm - Rock outcrop complex, extremely stony.",
    "28": "Leighcan family - Rock outcrop complex, extremely stony.",
    "29": "Como - Legault families complex, extremely stony.",
    "30": "Como family - Rock land - Legault family complex, extremely stony.",
    "31": "Leighcan - Catamount families complex, extremely stony.",
    "32": "Catamount family - Rock outcrop - Leighcan family complex, extremely stony.",
    "33": "Leighcan - Catamount families - Rock outcrop complex, extremely stony.",
    "34": "Cryorthents - Rock land complex, extremely stony.",
    "35": "Cryumbrepts - Rock outcrop - Cryaquepts complex.",
    "36": "Bross family - Rock land - Cryumbrepts complex, extremely stony.",
    "37": "Rock outcrop - Cryumbrepts - Cryorthents complex, extremely stony.",
    "38": "Leighcan - Moran families - Cryaquolls complex, extremely stony.",
    "39": "Moran family - Cryorthents - Leighcan family complex, extremely stony.",
    "40": "Moran family - Cryorthents - Rock land complex, extremely stony."
}

with open('form_field.pkl', 'wb') as fp:
    pickle.dump([
            dict(id='Elevation',name='Elevation',type='number',label='Elevation',value=2500,min=1859,max=3858),
            dict(id='Aspect',name='Aspect',type='number',label='Aspect',value=0,min=0,max=360),
            dict(id='Slope',name='Slope',type='number',label='Slope',value=0,min=0,max=66),
            dict(id='HDistHydr',name='HDistHydr',type='number',label='Horz. Dist. Water',value=0,min=0,max=1397),
            dict(id='VDistHydr',name='VDistHydr',type='number',label='Vert. Dist. Water',value=0,min=-173.,max=601),
            dict(id='HDistRoad',name='HDistRoad',type='number',label='Horz. Dist. Road',value=0,min=0,max=7117),
            dict(id='HillShade9am',name='HillShade9am',type='number',label='Hill Shade 9am',value=0,min=0,max=254),
            dict(id='HillShadeNoon',name='HillShadeNoon',type='number',label='Hill Shade Noon',value=0,min=0,max=254),
            dict(id='HillShade3pm',name='HillShade3pm',type='number',label='Hill Shade 3pm',value=0,min=0.,max=254),
            dict(id='HDistFire',name='HDistFire',type='number',label='Horz. Dist. Fire',value=0,min=0,max=7173),
            dict(id='WildArea',name='WildArea',type='select',label='Wild Area Type',
                 options=[{'value':n,'name':'Wild Area Type #%d' % (n,)} for n in range(1,5)]),
            dict(id='SoilType',name='SoilType',type='select',label='Soil Type',
                 options=[{'value':n,'name':soiltypes[str(n)]} for n in range(1,41)]),
            # Put OneHot encoded fields (comma separated) like this
            dict(type='text',name='onehot',value='WildArea,SoilType',hidden=True),
            # Put Randomizable fields (comma separated) like this. Please, make sure to give correct min/max values to each one before.
            dict(type='text',name='random',value='HDistFire,HillShade3pm,HillShadeNoon,HillShade9am,HDistRoad,VDistHydr,HDistHydr,Slope,Aspect,Elevation',hidden=True)
        ],
        fp
    )