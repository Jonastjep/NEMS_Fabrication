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

height = 4400
width = 5500

row1_y = 1550

chip << hbar.chip(height=height, width=width, chip_name='JT-HCT-001',layer=LAYER.ETCHA)

ypos = 900

a1 = hbar.HBAR_coupling_single_conn(separation=0.5,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << a1.move((0,0),(-1600,-ypos))
a2 = hbar.HBAR_coupling_single_conn(separation=1,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << a2.move((0,0),(-800,-ypos))
a3 = hbar.HBAR_coupling_single_conn(separation=5,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << a3.move((0,0),(0,-ypos))
a4 = hbar.HBAR_coupling_single_conn(separation=10,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << a4.move((0,0),(800,-ypos))
a5 = hbar.HBAR_coupling_single_conn(separation=20,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << a5.move((0,0),(1600,-ypos))

b1 = hbar.HBAR_coupling_single_conn(separation=2.5,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << b1.move((0,0),(-1600,-ypos)).rotate(180)
b2 = hbar.HBAR_coupling_single_conn(separation=7,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << b2.move((0,0),(-800,-ypos)).rotate(180)
b3 = hbar.HBAR_coupling_single_conn(separation=15,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << b3.move((0,0),(0,-ypos)).rotate(180)
b4 = hbar.HBAR_coupling_single_conn(separation=30,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << b4.move((0,0),(800,-ypos)).rotate(180)
b5 = hbar.HBAR_coupling_single_conn(separation=50,ramplink_length=400,layer_Aetch=LAYER.ETCHA,layer_Betch=LAYER.ETCHB,layer_alu=LAYER.AL,layer_alu_padding=LAYER.AL_PADDING,with_ant_padding=True).copy()
out << b5.move((0,0),(1600,-ypos)).rotate(180)

ground = gf.Component()
gnd = gf.components.rectangle(size=(400,3000),layer=LAYER.MISC,centered=True).copy()
ground.add_ref(gnd).movex(-2300)
ground.add_ref(gnd).movex(2300)
gnd_conn = gf.components.rectangle(size=(4600,400),layer=LAYER.MISC,centered=True).copy()
ground.add_ref(gnd_conn)

gnd_etch = ground.get_region(merge=True,layer=LAYER.MISC)
out.add_polygon(gnd_etch,layer=LAYER.ETCHB)

gnd_al = gf.components.rectangle(size=(400,3000),layer=LAYER.AL,centered=True).copy()
gnd_al.offset(layer=LAYER.AL, distance=-20)
out.add_ref(gnd_al).movex(-2300)
out.add_ref(gnd_al).movex(2300)

out.add_ref(chip)
out.rotate(angle=90,center=(0,0))

x1 = 1600
x2 = 1700

marker1 = gf.components.rectangle(size=(20,20),layer=LAYER.ETCHA,centered=True).copy()
out.add_ref(marker1).move((0,0),(-x1,2000))
out.add_ref(marker1).move((0,0),(x1,2000))
out.add_ref(marker1).move((0,0),(-x1,-2000))
out.add_ref(marker1).move((0,0),(x1,-2000))
out.add_ref(marker1).move((0,0),(x1,0))
out.add_ref(marker1).move((0,0),(-x1,0))

marker2 = gf.components.rectangle(size=(30,30),layer=LAYER.ETCHA,centered=True).copy()
out.add_ref(marker2).move((0,0),(-x2,2000))
out.add_ref(marker2).move((0,0),(x2,2000))
out.add_ref(marker2).move((0,0),(-x2,-2000))
out.add_ref(marker2).move((0,0),(x2,-2000))
out.add_ref(marker2).move((0,0),(-x2,0))
out.add_ref(marker2).move((0,0),(x2,0))

out.show()