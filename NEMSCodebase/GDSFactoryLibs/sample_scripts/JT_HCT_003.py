import gdsfactory as gf
import sys

from pathlib import Path
# Get the parent directory
parent_dir = Path(__file__).resolve().parent.parent
# Add parent directory to sys.path
sys.path.append(str(parent_dir))
import HBAR_lib as hbar

from gdsfactory.technology import LayerMap
from gdsfactory.typings import Layer
class LayerMapDemo(LayerMap):
    ETCHA: Layer = (1, 0)
    ETCHB: Layer = (2, 0)
    AL: Layer = (3,0)
    AL_PADDING: Layer = (4,0)
    MISC: Layer = (99,0)
LAYER = LayerMapDemo

print(LAYER.ETCHA)

out = gf.Component(name='HBAR_test_etch')

#Highest component, containing all objects
chip = gf.Component(name='HBAR_etch_test')

#We will make the chip contour, with names and chip name
contour = gf.Component(name='chip_contour')

height = 4000/2
width = 5600/2

row1_y = 1550

chip << hbar.chip(height=height, width=width, border_thick=30,text_size=100, chip_name='JT-HCT-003',layer=LAYER.ETCHA, single_sq_mkr=True)

seps = [5,7.5,10,20,50]
start = -1080
for sep in seps:

    a = hbar.HBAR_coupling_single_conn(separation=sep,
                                    ramplink_length=400,
                                    layer_Aetch=LAYER.ETCHA,
                                    layer_Betch=LAYER.ETCHB,
                                    layer_alu=LAYER.AL,
                                    layer_alu_padding=LAYER.AL_PADDING,
                                    with_ant_padding=True,
                                    padding_overlap = 1,
                                    ).copy()
    out << a.move((0,0),(start,0))
    start += 540

ground = gf.Component()
gnd = gf.components.rectangle(size=(400,1000),layer=LAYER.MISC,centered=True).copy()
ground.add_ref(gnd).movex(-2300)
ground.add_ref(gnd).movex(2300)
gnd_conn = gf.components.rectangle(size=(1500,400),layer=LAYER.MISC,centered=True).copy()
ground.add_ref(gnd_conn)

gnd_etch = ground.get_region(merge=True,layer=LAYER.MISC)
out.add_polygon(gnd_etch,layer=LAYER.ETCHB)

gnd_al = gf.components.rectangle(size=(400,3000),layer=LAYER.AL,centered=True).copy()
gnd_al.offset(layer=LAYER.AL, distance=-20)
out.add_ref(gnd_al).movex(-2300)
out.add_ref(gnd_al).movex(2300)

out.add_ref(chip)
out.rotate(angle=90,center=(0,0))

out.show()