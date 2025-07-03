import gdsfactory as gf
import numpy as np
from itertools import zip_longest

from gdsfactory.typings import ComponentSpec, PostProcesses, Size, Spacing


'''
In this library, the standard layer structure is as follows:
(1/0): Large structures
(2/0): Medium structures
(3/0): Small structures
(4/0): Fine structures
(5/0): Very fine structures
(6/0): Optional layer #1
(7/0): Markers
(8/0): Chip outline and text
'''

@gf.cell(check_instances=False)
def semi_circular_antenna(radius: float = 100, spacing: float = 30, layer: tuple = (2,0), layer1: tuple = (3,0), portwidth: float = 1, with_padding: bool = False, padding_overlap: float = 0) -> gf.Component:
 
    C = gf.components.circle(radius = radius, layer=layer)
    R = gf.components.rectangle(size=(radius,2*radius), layer=layer)

    temp = gf.Component()
    C1 = temp << C
    R1 = temp << R
    R1.movey(-radius)
    if with_padding:
        R2 = temp << R
        R2.movey(-radius)
        R2.movex(-0.08*radius)
        R3 = temp << R
        R3.movey(-radius)
        R3.movex(-0.08*radius+padding_overlap)

    antenna = gf.boolean(A=C1,B=R1,operation='not', layer=layer)

    if with_padding:
        padding = gf.boolean(A=antenna,B=R2,operation='and', layer=layer1,layer1=layer,layer2=layer)
        padding_overlap = gf.boolean(A=antenna,B=R3,operation='and', layer=layer1,layer1=layer,layer2=layer)
        antenna = gf.boolean(A=antenna,B=padding_overlap,operation='not', layer=layer,layer1=layer,layer2=layer1)

    sca = gf.Component()

    ant = gf.Component()
    ant << antenna
    if with_padding:
        ant << padding
    ant.add_port(name='e1',center=(-radius+portwidth/8,0),layer=layer,orientation=180,width=portwidth)

    ant1 = sca << ant
    ant2 = sca << ant
    ant2.rotate(angle = 180, center=(0,0))
    ant2.movex(spacing)

    sca.add_port('e1', port=ant1.ports['e1'])
    sca.add_port('e2', port=ant2.ports['e1'])
    
    sca.flatten()
    return sca


@gf.cell(check_instances=False)
def chip(width: float = 6000, 
         height: float = 5000, 
         border_thick: float = 100, 
         layer: tuple = (8,0), 
         grp_name: str = 'NEMS',
         chip_name: str = 'CHIP_NAME',
         version_nb: str = 'V_001',
         cp_nb: str = 'CP_000',
         text_size: float = 150,
         single_sq_mkr: bool = False,
         ) -> gf.Component:
    
    out = gf.components.rectangle(size=(width,height),centered=True,layer=layer)
    inn = gf.components.rectangle(size=(width-2*border_thick,height-2*border_thick),centered=True,layer=layer)

    border = gf.boolean(A=out,B=inn,operation='-',layer=layer)

    if not single_sq_mkr:
        marker_margin = 440+100
    else:
        marker_margin = 440/2+100
    txt_margin = 50

    grp_name = gf.components.text(text=grp_name,size=text_size,position=(-(width/2)+border_thick+txt_margin+marker_margin,-(height/2)+border_thick+txt_margin),layer=layer)
    chip_name = gf.components.text(text=chip_name,size=text_size,position=(-(width/2)+border_thick+txt_margin+marker_margin,(height/2)-border_thick-txt_margin-text_size),layer=layer)
    version_nb = gf.components.text(text=version_nb,size=text_size,position=((width/2)-border_thick-txt_margin-marker_margin,(height/2)-border_thick-txt_margin-text_size),justify='right',layer=layer)
    cp_nb = gf.components.text(text=cp_nb,size=text_size,position=((width/2)-border_thick-txt_margin-marker_margin,-(height/2)+border_thick+txt_margin),justify='right',layer=layer)

    outline = gf.Component()

    outline << border
    for text in [grp_name,chip_name,version_nb,cp_nb]: outline << text 

    marker = maker_double_square(layer=layer,single_sq=single_sq_mkr)
    outline.add_ref(marker).move((-(width/2)+border_thick+marker_margin/2,-(height/2)+border_thick+marker_margin/2))
    outline.add_ref(marker).move((-(width/2)+border_thick+marker_margin/2,(height/2)-border_thick-marker_margin/2))
    outline.add_ref(marker).move(((width/2)-border_thick-marker_margin/2,(height/2)-border_thick-marker_margin/2))
    outline.add_ref(marker).move(((width/2)-border_thick-marker_margin/2,-(height/2)+border_thick+marker_margin/2))

    outline.flatten()
    return outline

@gf.cell(check_instances=False)
def sub_text(component: ComponentSpec = "pad",
             text: str = 'subtext',
             text_size: float = 10,
             margin: float = 10,
             layer: tuple = (2,0)
             ) -> gf.Component:
    
    c = gf.Component()
    component = gf.get_component(component)
    bbox_coord = component.bbox_np()
    bottom = bbox_coord[0,1]
    c << component
    c << gf.components.text(text=text,size=text_size,position=(0,bottom-text_size-margin),justify='center', layer=layer)
    c.flatten()
    return c

@gf.cell(check_instances=False)
def maker_double_square(layer: tuple = (7,0), core_size: float = 20, single_sq: bool = False) -> gf.Component:
    c = gf.Component()

    core = gf.components.rectangle(size=(core_size,core_size),centered=True,layer=layer)
    c << core

    quadrant = gf.Component()
    small_corner = gf.components.L(width=20,size=(90,90),layer=layer)
    sc = quadrant << small_corner
    sc.move((-100,-100))

    if not single_sq:
        large_corner = gf.components.L(width=40,size=(180,180),layer=layer)
        lc = quadrant << large_corner
        lc.move((-200,-200))

    for i in range(4): c.add_ref(quadrant).rotate(angle=90*i, center=(0,0))

    c.flatten()

    return c

@gf.cell(check_instances=False)
def component_padding(component: ComponentSpec = "pad",
                      layer: tuple = (10,0),
                      interm_layer: tuple = (25,0),
                      offset_size: float = 50,
                      offset_OvUn: float = 0.2,
                      ) -> gf.Component:
    
    c = component.copy()
    c.flatten()

    remap_pairs_l = [{x[0]:x[1]} for x in list(zip_longest(c.layers,[],fillvalue=interm_layer))]
    remap_pairs = {k: v for d in remap_pairs_l for k, v in d.items()}

    c.remap_layers(remap_pairs)
    c.flatten()
    c.offset(layer=interm_layer,distance=offset_size)
    c.over_under(layer=interm_layer,distance=offset_OvUn)
    c.remap_layers({interm_layer: layer})

    return c

@gf.cell(check_instances=False)
def empty_chip_space(chip: ComponentSpec = "pad",
                      layer: tuple = (10,0),
                      interm_layer: tuple = (25,0),
                      offset_size: float = 50,
                      offset_OvUn: float = 10,
                      ) -> gf.Component:
    
    padding = component_padding(chip,layer=layer,interm_layer=interm_layer,offset_OvUn=offset_OvUn,offset_size=offset_size)

    c = chip.copy()
    c.flatten()

    remap_pairs_l = [{x[0]:x[1]} for x in list(zip_longest(c.layers,[],fillvalue=interm_layer))]
    remap_pairs = {k: v for d in remap_pairs_l for k, v in d.items()}

    c.remap_layers(remap_pairs)
    chip_bbox = gf.components.bbox(component=c,layer=interm_layer).copy()

    chip_bbox.remap_layers({interm_layer: layer})

    out = gf.boolean(A=chip_bbox,B=padding,operation='-',layer=layer)

    return out

@gf.cell(check_instances=False)
def chip_fill_fluxtraps(chip: ComponentSpec = "pad",
                      layer: tuple = (10,0),
                      interm_layer: tuple = (25,0),
                      offset_size: float = 50,
                      offset_OvUn: float = 10,
                      trap_size: float = 20,
                      trap_sep: float = 20,
                      ) -> gf.Component:
    
    c = gf.Component()

    width = chip.dxsize
    height = chip.dysize

    chip = chip.copy()

    empty_space = empty_chip_space(chip=chip,layer=layer,interm_layer=interm_layer,offset_size=offset_size,offset_OvUn=offset_OvUn)

    nb_cols = width/(trap_size+trap_sep) +1
    nb_rows = height/(trap_size+trap_sep) +1
    
    trap = gf.components.rectangle((trap_size,trap_size),layer=layer)
    fluxTrap_array = gf.components.containers.array(trap,
                                                    columns=nb_cols,
                                                    column_pitch=trap_sep+trap_size,
                                                    rows=nb_rows,
                                                    row_pitch=trap_sep+trap_size,
                                                    centered=True)

    r1 = empty_space.get_region(layer=layer)
    r2 = fluxTrap_array.get_region(layer=layer)

    # #Referenced for other methods
    # r_overlap = r2.select_overlapping(r1) #page 349 of klayout manual: https://www.klayout.de/doc-qt5/klayout.pdf
    # r_overlap = r2.select_not_overlapping(r1) 
    # r3 = r1.or_(r_overlap)

    r_overlap = r2.select_inside(r1)

    c.add_polygon(r_overlap,layer=layer)
    # c << empty_space

    return c


@gf.cell(check_instances=False)
def rect_space_dose_test(layer: tuple = (10,0),
                      rect_width: float = 50,
                      rect_height: float = 200,
                      separation: float = 20,
                      ) -> gf.Component:
    
    c = gf.Component()

    rect1 = gf.components.rectangle(size=(rect_width,rect_height),layer=layer,centered=True)
    rect2 = gf.components.rectangle(size=(rect_width,rect_height),layer=layer,centered=True)

    r1 = c << rect1
    r2 = c << rect2

    r1.movex(origin=0,destination=-rect_width/2-separation/2)
    r2.movex(origin=0,destination=rect_width/2+separation/2)

    return c

@gf.cell(check_instances=False)
def HBAR_coupling_single_conn(baselayer: tuple = (10,0),
                            antenna_radius: float = 100,
                            pad_width: float = 400,
                            pad_height: float = 300,
                            ramp_length: float = 50,
                            ramp_base: float = 100,
                            separation: float = 20,
                            layer_alu: tuple = (1,0),
                            layer_alu_padding: tuple = (2,0),
                            layer_Aetch: tuple = (3,0),
                            layer_Betch: tuple = (4,0),
                            Aetch_padding: float = 100,
                            Betch_padding: float = 5,
                            portwidth: float = 2,
                            ramplink_width: float = 10,
                            ramplink_length: float = 600,
                            with_text: bool = True,
                            with_etch: bool = True,
                            with_ant_padding: bool = False,
                            padding_overlap: float = 1,
                            text_size: float = 50,
                            ) -> gf.Component:
    
    aluminium = gf.Component()

    ant = semi_circular_antenna(radius=antenna_radius,spacing=separation,layer=layer_alu, layer1=layer_alu_padding,portwidth=portwidth,with_padding=with_ant_padding,padding_overlap=padding_overlap)
    a1 = aluminium.add_ref(ant.copy().rotate(90))

    ramplink = gf.components.taper(length=ramplink_length, width1=ramplink_width, width2=portwidth, port=None, layer=layer_alu)
    rl1 = aluminium.add_ref(ramplink)
    rl1.connect('o2', other=a1['e1'])

    ramp = gf.components.taper(length=ramp_length, width1=ramp_base, width2=ramplink_width, port=None, layer=layer_alu)
    r1 = aluminium.add_ref(ramp)
    r1.connect('o2', other=rl1['o1'])

    pad = gf.components.rectangle(size=(pad_width,pad_height),centered=True,layer=layer_alu).copy()
    pad.add_port('p1',center=(0,pad_height/2),width=ramp_base,orientation=90,layer=layer_alu)
    p1 = aluminium.add_ref(pad)
    p1.connect('p1', other=r1['o1'])

    if with_etch:
        etch_A = gf.Component()
        ae = gf.components.rectangle(size=(pad_width+1.2*Aetch_padding, pad_height+ramp_length+ramplink_length+Aetch_padding), centered=True, layer=layer_Aetch)
        ae = etch_A.add_ref(ae).movey(-(pad_height+ramp_length+ramplink_length+Aetch_padding)/2-antenna_radius-Aetch_padding/6)

        #Temp antenna for successfully doing the padding offset, as they need to be in the same layer for that
        temp_aluminium = gf.Component()
        temp_layer = (99,0)
        ant_temp = semi_circular_antenna(radius=antenna_radius,spacing=separation,layer=temp_layer, layer1=temp_layer,portwidth=portwidth,with_padding=with_ant_padding)
        a1_temp = temp_aluminium.add_ref(ant_temp.copy().rotate(90))
        ramplink_temp = gf.components.taper(length=ramplink_length, width1=ramplink_width, width2=portwidth, port=None, layer=temp_layer)
        rl1_temp = temp_aluminium.add_ref(ramplink_temp)
        rl1_temp.connect('o2', other=a1_temp['e1'])
        ramp_temp = gf.components.taper(length=ramp_length, width1=ramp_base, width2=ramplink_width, port=None, layer=temp_layer)
        r1_temp = temp_aluminium.add_ref(ramp_temp)
        r1_temp.connect('o2', other=rl1_temp['o1'])

        etch_B = gf.Component()
        be = gf.components.rectangle(size=(3*antenna_radius,3*antenna_radius), centered=True, layer=layer_Betch)
        be = etch_B.add_ref(be).movey(separation/2)
        etch_B = gf.boolean(etch_B,temp_aluminium,'-',layer=layer_Betch,layer1=layer_Betch,layer2=temp_layer)
        etch_B.offset(layer=layer_Betch,distance=-Betch_padding)

    out = gf.Component()
    out << aluminium
    if with_etch:
        out << etch_A
        out << etch_B
    if with_text:
        out << gf.components.text(text='s='+str(separation)+',r='+str(antenna_radius),size=text_size,position=(0,-out.dysize+0.8*antenna_radius),justify='center', layer=layer_alu)
    out.move(out.center,(0,0))

    return out
