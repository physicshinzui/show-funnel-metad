import math
import sys
import numpy as np
from pymol import cmd

def read_plumed_input(filename):
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line.startswith('#'): continue 
            if '=' not in line: continue 
            
            elems = line.split('=')
            
            if elems[0] == 'ZCC':
                zcc = float(elems[1]) * 10 # nm to Angstrom

            elif elems[0] == 'ALPHA':
                alpha = float(elems[1])
            
            elif elems[0] == 'RCYL':
                Rcyl = float(elems[1]) * 10 # nm to Angstrom
            
            elif elems[0] == 'POINTS':
                ## Convert nm to Angstrom for PyMOL
                point1 = np.array([float(x) * 10 for x in elems[1].split(',')[0:3]])
                point2 = np.array([float(x) * 10 for x in elems[1].split(',')[3:6]])
            
    return zcc, alpha, Rcyl, point1, point2

def view_funnel(zcc, alpha, Rcyl, point1, point2):
    R_bottom = float(zcc) * math.tan(alpha) + Rcyl
    radii = [R_bottom, Rcyl]
    color0 = [1.0, 1.0, 0.0]
    color1 = [1.0, 1.0, 0.0]
    caps = [0, 0]

    # axis vector which is the center of the funnel 
    vec_along_axis = point2 - point1
    unit_vec = vec_along_axis / np.linalg.norm(vec_along_axis)
    point1 = point1.tolist()
    point2 = point2.tolist()
    funnel_end_point = point1 + zcc * unit_vec 
    funnel_end_point = funnel_end_point.tolist()
    cone = [cgo.CONE] + point1 + funnel_end_point + radii + color0 + color1 + caps
    cmd.load_cgo(cone, "cone")
    cmd.set("cgo_transparency", 0.5, 'cone')

    # Translate point 2 along vec_axis
    point_cyl_end = funnel_end_point + 10.0*unit_vec  # 5.0 is a magic number
    point_cyl_end = point_cyl_end.tolist()
    cyl = [cgo.CONE] + funnel_end_point + point_cyl_end + [Rcyl, Rcyl] + color0 + color1 + caps
    # cyl = [cgo.CYLINDER, *funnel_end_point, *point_cyl_end, Rcyl, *color0, *color1, *caps]
    cmd.load_cgo(cyl, "cylinder")
    cmd.set("cgo_transparency", 0.5, 'cylinder')

    return unit_vec

def draw_line(point1, point2, name):
    color = [1.0, 1.0, 1.0]
    caps = [0,0]
    line = [cgo.CONE] + point1 + point2 + [0.1,0.1] + color + color + caps
    cmd.load_cgo(line, name)
    cmd.set("cgo_transparency", 0.0, name)

def main():
    help=f"""
    Usage: 
        pymol {sys.argv[0]} -- [reference pdb] [plumed input] [ligand name]
    """
    print(help)
    ref = sys.argv[1] 
    filename = sys.argv[2] 
    ligname = sys.argv[3]
    cmd.load(f"{ref}")

    zcc, alpha, Rcyl, point1, point2 = read_plumed_input(filename)
    print(f"Zcc = {zcc}, alpha = {alpha}, Rcyl = {Rcyl}, Point1 = {point1}, Point 2 = {point2}")
    unit_vec_along_axis = view_funnel(zcc, alpha, Rcyl, point1, point2)

    lig_com = cmd.centerofmass(f"resname {ligname}")
    lig_com_frm_point1 = lig_com - point1
    proj = np.dot(unit_vec_along_axis, lig_com_frm_point1)
    print(f"Projection along the axis = {proj:10.3f} Angstrom")
    proj_point = proj*unit_vec_along_axis + point1
    cmd.pseudoatom('plig', pos=lig_com)
    cmd.pseudoatom('pp',pos=proj_point.tolist())
    cmd.pseudoatom('p1',pos=point1.tolist())
    axis_end = 3*proj*unit_vec_along_axis + point1
    draw_line(lig_com, proj_point.tolist(), 'proj')
    draw_line(point1.tolist(), axis_end.tolist(), 'axis')
    cmd.distance('lp', 'plig', 'pp')
    cmd.distance('ld', 'p1', 'pp')

main()
