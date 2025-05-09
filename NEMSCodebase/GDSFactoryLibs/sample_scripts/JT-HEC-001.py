import gdsfactory as gf
import HBAR_lib as hbar
from itertools import zip_longest

from gdsfactory.technology import (
    LayerMap,
)
from gdsfactory.typings import Layer

out = gf.Component(name='JT-HEC-001')

#Highest component, containing all objects
chip = gf.Component(name='JT-HEC-001t')

#We will make the chip contour, with names and chip name
contour = gf.Component(name='chip_contour')

height = 4400
width = 5500

row1_y = 1550

class LayerMap(LayerMap):
    ETCH1_BEAM1: Layer = (1, 0)
    ETCH1_BEAM2: Layer = (2, 0)

LAYER = LayerMap
gf.kcl.layers = LAYER

chip << hbar.chip(height=height, width=width, chip_name='JT-HEC-001',layer=LAYER.ETCH1_BEAM1)

doses = []
for spacing in [0.5,1,1.5,2,3,4,5,6,7,8,9,10,20,30,50]:
    dose = hbar.rect_space_dose_test(separation=spacing, rect_height=120,layer=LAYER.ETCH1_BEAM2)
    # a.add_label(text = spacing)
    doses.append(hbar.sub_text(dose, text=str(spacing)+' um',layer=LAYER.ETCH1_BEAM2))
dose_grid = gf.grid(
    tuple(doses),
    shape=(3,5),
    spacing=(50,50),
    align_x='center',
    align_y='center',
)
d1 = chip << dose_grid
d1.move(origin=d1.center,destination=(-(width/2)/2,row1_y))
d1.flatten()

rects = []
arr1 = [10,20,30,40,50]
arr2 = [1,5,10,20,30,40,50,60,80,100]
for s1 in arr1:
    for s2 in arr2:
        rect = gf.components.rectangle(size=(s2,s1),layer=LAYER.ETCH1_BEAM2,centered=True)
        rects.append(hbar.sub_text(rect, text='('+str(s1)+','+str(s2)+') um',layer=LAYER.ETCH1_BEAM2))
rect_grid = gf.grid(
    tuple(rects),
    shape=(len(arr1),len(arr2)),
    spacing=(50,50),
    align_x='center',
    align_y='center',
)
r1 = chip << rect_grid
r1.move(origin=r1.center,destination=(0,row1_y))
r1.flatten()

ellis = []
arr1 = [10,20,30,40]
arr2 = [10,20,30,40,50,70]
for s1 in arr1:
    for s2 in arr2:
        elli = gf.components.ellipse(radii=(s2,s1),layer=LAYER.ETCH1_BEAM2)
        ellis.append(hbar.sub_text(elli, text='('+str(s1)+','+str(s2)+') um',layer=LAYER.ETCH1_BEAM2))
elli_grid = gf.grid(
    tuple(ellis),
    shape=(len(arr1),len(arr2)),
    spacing=(50,50),
    align_x='center',
    align_y='center',
)
e1 = chip << elli_grid
e1.move(origin=e1.center,destination=((width/2)/2,row1_y))
e1.flatten()

h = 1300
w = 2300
chip.add_ref(hbar.maker_double_square(layer=LAYER.ETCH1_BEAM1,core_size=30)).move(origin=(0,0),destination=(-w,h))
chip.add_ref(hbar.maker_double_square(layer=LAYER.ETCH1_BEAM1,core_size=30)).move(origin=(0,0),destination=(w,h))
chip.add_ref(hbar.maker_double_square(layer=LAYER.ETCH1_BEAM1,core_size=30)).move(origin=(0,0),destination=(-w,-h))
chip.add_ref(hbar.maker_double_square(layer=LAYER.ETCH1_BEAM1,core_size=30)).move(origin=(0,0),destination=(w,-h))

out.add_ref(chip).rotate(angle=90,center=(0,0))

out.show()