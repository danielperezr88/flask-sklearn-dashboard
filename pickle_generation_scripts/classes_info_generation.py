#!/usr/bin/python
# -*- coding: latin-1 -*-
# Classes info example: Agro Model

import pickle
from os import path

names = ['Romana',
 'Iceberg',
 'Trocadero',
 'Hoja de roble',
 'Lollo rosso',
 'Radiccio',
 'Escarola',
 'Endivia',
 'Canónigo',
 'Rúcula']

images = ['Romana',
 'Iceberg',
 'Trocadero',
 'Hoja de roble',
 'Lollo rosso',
 'Radiccio',
 'Escarola',
 'Endivia',
 'Canónigo',
 'Rúcula']

descriptions = ['Alargada y de hoja no muy apretada al tronco. ',
 'Redonda y de hojas muy prietas y crujientes.',
 'Hojas tiernas, también conocida como francesa.',
 'Hojas onduladas de de distintas tonalidades, del verde al morado.',
 'Sabor algo amargo, hojas muy rizadas e intenso color rojo.',
 'Achicoria roja, de hojas rojas y algo amargas.',
 'Puede ser rizada o francesa, con ligero sabor amargo.',
 'Hoja tersa y blanca, con sabor dulce y cierto fondo amargo.',
 'Hojas pequeñitas, pero de sabor intenso y gran ricas en hierro.',
 'Cierto sabor picante, combina con otras lechugas más suaves.']

# All fields are mandatory
with open(path.join('..','model','classes_info.pkl'), 'wb') as fp:
    pickle.dump(dict(
            names={
                '1': names[0],
                '2': names[1],
                '3': names[2],
                '4': names[3],
                '5': names[4],
                '6': names[5],
                '7': names[6]
            },
            images={
                '1': images[0],
                '2': images[1],
                '3': images[2],
                '4': images[3],
                '5': images[4],
                '6': images[5],
                '7': images[6]
            },
            descriptions={
                '1': descriptions[0],
                '2': descriptions[1],
                '3': descriptions[2],
                '4': descriptions[3],
                '5': descriptions[4],
                '6': descriptions[5],
                '7': descriptions[6]
            }
        ),
        fp
    )