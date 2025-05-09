import gdsfactory as gf
import HBAR_lib as hbar
from itertools import zip_longest

#Highest component, containing all objects
chip = gf.Component(name='JT-DT_SCA-001')

#We will make the chip contour, with names and chip name
contour = gf.Component(name='chip_contour')

height = 4800
width = 5800

c = contour << hbar.chip(height=height, width=width, chip_name='JT-DT_SCA-001')

#Now we make the content of the chip: the dose test array
content = gf.Component(name = 'dose_test_array')

antenna_radius = 100
portwidth = 1

antennas = []
for spacing in [i/10 for i in range(1,20)]:
    ant = hbar.semi_circular_antenna(radius=antenna_radius,spacing=spacing,portwidth=portwidth,with_padding=True)
    # a.add_label(text = spacing)
    antennas.append(hbar.sub_text(ant, text=str(spacing*1000)+' nm'))

ant_grid = gf.grid(
    tuple(antennas),
    spacing=(50,50),
    align_x='x',
    align_y='y'
)

grid_array = gf.components.array(component=ant_grid,columns=1,rows=10,row_pitch=300,centered=True) 
cont = content << grid_array
cont.flatten()

chip.add_ref(contour).rotate(angle=90,center=(0,0))
chip.add_ref(content).rotate(angle=90,center=(0,0))

# #add empty space polygons for flux traps
# empty_space = hbar.empty_chip_space(chip=chip,offset_size=100,offset_OvUn=10)
# chip << empty_space

flux_traps = hbar.chip_fill_fluxtraps(chip=chip)
chip << flux_traps

#push the full chip design to KLayout
chip.show()

