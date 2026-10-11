import pcbnew
import math
import re

board = pcbnew.BOARD()
board_w, board_h = 100.0, 70.0
def mm(v): return pcbnew.FromMM(v)

# Board design settings: clearance 0.15mm, track min width 0.15mm
ds = board.GetDesignSettings()
ds.m_MinClearance = pcbnew.FromMM(0.15)
ds.m_TrackMinWidth = pcbnew.FromMM(0.15)
default_nc = ds.m_NetSettings.GetDefaultNetclass()
default_nc.SetClearance(pcbnew.FromMM(0.15))
default_nc.SetTrackWidth(pcbnew.FromMM(0.2))

# 1. Edge Cuts
pts = [(0, 0), (board_w, 0), (board_w, board_h), (0, board_h)]
for i in range(4):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(pts[i][0], pts[i][1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(pts[(i+1)%4][0], pts[(i+1)%4][1]))
    seg.SetWidth(mm(0.15))
    board.Add(seg)

# 2. M3 Holes
for idx, (hx, hy) in enumerate([(4.0, 4.0), (4.0, 66.0), (96.0, 4.0), (96.0, 66.0)]):
    fp_hole = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
    fp_hole.SetReference(f'H{idx+1}')
    fp_hole.Reference().SetVisible(False)
    fp_hole.Value().SetVisible(False)
    fp_hole.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
    board.Add(fp_hole)

# 3. Parse Netlist
with open('pcb/main_board/main_board.net') as f:
    netlist_text = f.read()

net_pins = {}
nets = {}
for m in re.finditer(r'\(net\s+\(code\s+\"(\d+)\"\)\s+\(name\s+\"([^\"]+)\"\)(.*?)(?=\n\t\t\(net|\n\t\))', netlist_text, re.DOTALL):
    code, name, body = m.group(1), m.group(2), m.group(3)
    net_item = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net_item)
    nets[name] = board.FindNet(name)
    pins = []
    for pm in re.finditer(r'\(node\s+\(ref\s+\"([^\"]+)\"\)\s+\(pin\s+\"([^\"]+)\"\)', body):
        pins.append((pm.group(1), pm.group(2)))
    net_pins[name] = pins

def place_fp(pretty_path, fp_name, ref, val, x, y, rot_deg=0):
    fp = pcbnew.FootprintLoad(pretty_path, fp_name)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.Value().SetVisible(False)
    fp.Reference().SetVisible(False)
    for t in fp.GraphicalItems():
        if isinstance(t, pcbnew.PCB_TEXT):
            t.SetVisible(False)
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    board.Add(fp)
    return fp

j1 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J1', 'Line_In', 15.0, 10.0, 180)
j2 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J2', 'Speaker_Out', 53.0, 10.0, 180)
j3 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J3', 'Headphone_Out', 86.0, 10.0, 180)

c1 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C1', '4.7uF', 12.0, 22.0, 0)
c2 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C2', '4.7uF', 20.0, 22.0, 0)
u2 = place_fp('/usr/share/kicad/footprints/Package_DIP.pretty', 'DIP-20_W7.62mm', 'U2', 'PT2258', 28.0, 22.0, 0)

r2 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R2', '4.7k', 12.0, 32.5, 0)
r1 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R1', '4.7k', 12.0, 38.0, 0)

c4 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C4', '4.7uF', 42.0, 20.0, 0)
c3 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C3', '4.7uF', 42.0, 26.0, 0)
c8 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C8', '10uF', 42.0, 32.0, 0)

c6 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D6.3mm_P2.50mm', 'C6', '100uF', 54.0, 24.0, 0)
c7 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'C_Disc_D4.3mm_W1.9mm_P5.00mm', 'C7', '0.1uF', 54.0, 29.5, 0)
l1 = place_fp('/usr/share/kicad/footprints/Inductor_THT.pretty', 'L_Axial_L7.0mm_D3.3mm_P10.16mm_Horizontal_Fastron_MICC', 'L1', '10uH', 54.0, 35.0, 0)

ry1 = place_fp('/usr/share/kicad/footprints/Relay_THT.pretty', 'Relay_DPDT_Omron_G6K-2P-Y', 'RY1', 'G6K-2P-Y_DC5', 68.0, 25.0, 90)

d1 = place_fp('/usr/share/kicad/footprints/Diode_THT.pretty', 'D_DO-35_SOD27_P7.62mm_Horizontal', 'D1', '1N4148', 82.0, 21.0, 0)
q1 = place_fp('/usr/share/kicad/footprints/Package_TO_SOT_THT.pretty', 'TO-92_Inline', 'Q1', '2N7000', 82.0, 26.0, 0)
rg = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R_G', '1k', 82.0, 32.0, 0)
r3 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R3', '10k', 68.0, 34.0, 0)

nt1 = place_fp('/usr/share/kicad/footprints/NetTie.pretty', 'NetTie-2_THT_Pad1.0mm', 'NT1', 'NetTie_2', 5.0, 36.0, 270)

j4 = place_fp('/usr/share/kicad/footprints/Connector_RJ.pretty', 'RJ45_Amphenol_RJHSE5380', 'J4', 'RJ45_Satellite', 14.0, 56.0, 0)
u1 = place_fp('pcb/main_board/main_board_footprints.pretty', 'XIAO_ESP32C6_Socket', 'U1', 'XIAO_ESP32C6', 86.0, 52.0, 180)
c5 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'C_Disc_D4.3mm_W1.9mm_P5.00mm', 'C5', '0.1uF', 70.0, 54.54, 180)

fp_by_ref = {
    'J1': j1, 'J2': j2, 'J3': j3, 'J4': j4, 'U1': u1, 'U2': u2,
    'RY1': ry1, 'C1': c1, 'C2': c2, 'C3': c3, 'C4': c4, 'C8': c8,
    'Q1': q1, 'D1': d1, 'R_G': rg, 'R3': r3,
    'L1': l1, 'C6': c6, 'C7': c7, 'C5': c5, 'R1': r1, 'R2': r2,
    'NT1': nt1
}

for net_name, pins in net_pins.items():
    if net_name not in nets: continue
    net_obj = nets[net_name]
    for ref, pin_num in pins:
        if ref in fp_by_ref:
            for pad in fp_by_ref[ref].Pads():
                if pad.GetNumber() == pin_num:
                    pad.SetNet(net_obj)

for pad in j4.Pads():
    if pad.GetNumber() == 'SH':
        pad.SetNet(nets['DGND'])

def pad_pos(fp, pad_num):
    for p in fp.Pads():
        if p.GetNumber() == str(pad_num):
            pos = p.GetPosition()
            return (round(pos.x / 1e6, 3), round(pos.y / 1e6, 3))
    raise ValueError(f"Pad {pad_num} not found on {fp.GetReference()}")

def add_track(x1, y1, x2, y2, net, layer=pcbnew.F_Cu, width_mm=0.25):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
    t.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
    t.SetWidth(mm(width_mm))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)

def add_path(pts, net, layer=pcbnew.F_Cu, width_mm=0.25):
    for i in range(len(pts) - 1):
        if pts[i] != pts[i+1]:
            add_track(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net, layer, width_mm)

def add_via(x, y, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    v.SetWidth(mm(0.8))
    v.SetDrill(mm(0.4))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)

# ----------------- 1. Audio Routing -----------------
p_j1_t = pad_pos(j1, 'T'); p_c1_1 = pad_pos(c1, '1')
add_path([p_j1_t, (10.0, 18.0), (12.0, 18.0), p_c1_1], nets['/LINE_IN_L'], pcbnew.F_Cu, 0.3)

p_j1_r = pad_pos(j1, 'R'); p_c2_1 = pad_pos(c2, '1')
add_path([p_j1_r, p_c2_1], nets['/LINE_IN_R'], pcbnew.B_Cu, 0.3)

p_c1_2 = pad_pos(c1, '2'); p_u2_1 = pad_pos(u2, '1')
add_path([p_c1_2, (14.5, 20.0), (28.0, 20.0), p_u2_1], nets['/VOL_IN_L'], pcbnew.F_Cu, 0.3)

p_c2_2 = pad_pos(c2, '2'); p_u2_2 = pad_pos(u2, '2')
add_path([p_c2_2, (25.0, p_c2_2[1]), (25.0, p_u2_2[1]), p_u2_2], nets['/VOL_IN_R'], pcbnew.F_Cu, 0.3)

p_u2_15 = pad_pos(u2, '15'); p_c8_1 = pad_pos(c8, '1')
add_path([p_u2_15, (39.0, p_u2_15[1]), (39.0, p_c8_1[1]), p_c8_1], nets['Net-(U2-REF)'], pcbnew.F_Cu, 0.3)

# R ch: U2 Pin 19 -> C4 on F.Cu
p_u2_19 = pad_pos(u2, '19'); p_c4_1 = pad_pos(c4, '1')
add_path([p_u2_19, (37.0, p_u2_19[1]), (37.0, p_c4_1[1]), p_c4_1], nets['/VOL_OUT_R'], pcbnew.F_Cu, 0.3)

# L ch: U2 Pin 20 -> C3 on B.Cu
p_u2_20 = pad_pos(u2, '20'); p_c3_1 = pad_pos(c3, '1')
add_path([p_u2_20, (39.0, p_u2_20[1]), (39.0, p_c3_1[1]), p_c3_1], nets['/VOL_OUT_L'], pcbnew.B_Cu, 0.3)

# COM_R (R ch): C4 Pin 2 -> RY1 Pin 6 on B.Cu at Y=18.0, hopping over RELAY_COIL_NEG at X=68.0 via F.Cu jumper
p_c4_2 = pad_pos(c4, '2'); p_ry_6 = pad_pos(ry1, '6')
add_path([p_c4_2, (p_c4_2[0], 18.0), (66.5, 18.0)], nets['/COM_R'], pcbnew.B_Cu, 0.3)
add_via(66.5, 18.0, nets['/COM_R'])
add_path([(66.5, 18.0), (69.5, 18.0)], nets['/COM_R'], pcbnew.F_Cu, 0.3)
add_via(69.5, 18.0, nets['/COM_R'])
add_path([(69.5, 18.0), (p_ry_6[0], 18.0), p_ry_6], nets['/COM_R'], pcbnew.B_Cu, 0.3)

# COM_L (L ch): C3 Pin 2 -> RY1 Pin 3 on B.Cu via Y=27.5 directly to Pin 3
p_c3_2 = pad_pos(c3, '2'); p_ry_3 = pad_pos(ry1, '3')
add_path([p_c3_2, (p_c3_2[0], 27.5), (p_ry_3[0], 27.5), p_ry_3], nets['/COM_L'], pcbnew.B_Cu, 0.3)

# SPK_OUT_R (R ch): RY1 Pin 7 -> north to Y=17.0 -> west to J2 Pad R (57.0, 10.0) on F.Cu
p_ry_7 = pad_pos(ry1, '7'); p_j2_r = pad_pos(j2, 'R')
add_path([p_ry_7, (p_ry_7[0], 17.0), (p_j2_r[0], 17.0), p_j2_r], nets['/SPK_OUT_R'], pcbnew.F_Cu, 0.3)

# SPK_OUT_L (L ch): RY1 Pin 2 -> north to Y=22.0 -> F.Cu with short B.Cu jumper around X=66.0
p_ry_2 = pad_pos(ry1, '2'); p_j2_t = pad_pos(j2, 'T')
add_path([p_ry_2, (p_ry_2[0], 22.0), (67.5, 22.0)], nets['/SPK_OUT_L'], pcbnew.F_Cu, 0.3)
add_via(67.5, 22.0, nets['/SPK_OUT_L'])
add_path([(67.5, 22.0), (64.5, 22.0)], nets['/SPK_OUT_L'], pcbnew.B_Cu, 0.3)
add_via(64.5, 22.0, nets['/SPK_OUT_L'])
add_path([(64.5, 22.0), (p_j2_t[0], 22.0), p_j2_t], nets['/SPK_OUT_L'], pcbnew.F_Cu, 0.3)

# HP_OUT_R (R ch): RY1 Pin 5 -> north to Y=16.5 -> east to J3 Pad R (88.0, 10.0) on F.Cu
p_ry_5 = pad_pos(ry1, '5'); p_j3_r = pad_pos(j3, 'R')
add_path([p_ry_5, (76.0, p_ry_5[1]), (76.0, 16.5), (p_j3_r[0], 16.5), p_j3_r], nets['/HP_OUT_R'], pcbnew.F_Cu, 0.3)

# HP_OUT_L (L ch): RY1 Pin 4 -> B.Cu route north to J3 Pad T (84.0, 10.0)
p_ry_4 = pad_pos(ry1, '4'); p_j3_t = pad_pos(j3, 'T')
add_path([p_ry_4, (78.0, p_ry_4[1]), (78.0, 14.5), (p_j3_t[0], 14.5), p_j3_t], nets['/HP_OUT_L'], pcbnew.B_Cu, 0.3)

# ----------------- 2. Relay Driver -----------------
# RELAY_COIL_NEG: RY1 Pin 8 (68.0, 19.92) to D1 Pad 2 (89.62, 21.0) on B.Cu North at Y=13.0
p_ry_8 = pad_pos(ry1, '8'); p_d1_2 = pad_pos(d1, '2'); p_q1_3 = pad_pos(q1, '3')
add_path([p_ry_8, (68.0, 13.0), (89.62, 13.0), p_d1_2], nets['/RELAY_COIL_NEG'], pcbnew.B_Cu, 0.3)
add_path([p_d1_2, (p_d1_2[0], 26.0), p_q1_3], nets['/RELAY_COIL_NEG'], pcbnew.F_Cu, 0.3)

# Net-(Q1-G): Q1 Pin 2 -> R_G Pin 2 on F.Cu; R_G Pin 2 to R3 Pad 1 (68.0, 34.0) via B.Cu jumper Y=36.5
p_q1_2 = pad_pos(q1, '2'); p_rg_2 = pad_pos(rg, '2'); p_r3_1 = pad_pos(r3, '1')
add_path([p_q1_2, (p_q1_2[0], 29.0), (p_rg_2[0], 29.0), p_rg_2], nets['Net-(Q1-G)'], pcbnew.F_Cu, 0.25)
add_via(p_rg_2[0], 36.5, nets['Net-(Q1-G)'])
add_path([p_rg_2, (p_rg_2[0], 36.5)], nets['Net-(Q1-G)'], pcbnew.F_Cu, 0.25)
add_path([(p_rg_2[0], 36.5), (p_r3_1[0], 36.5)], nets['Net-(Q1-G)'], pcbnew.B_Cu, 0.25)
add_via(p_r3_1[0], 36.5, nets['Net-(Q1-G)'])
add_path([(p_r3_1[0], 36.5), p_r3_1], nets['Net-(Q1-G)'], pcbnew.F_Cu, 0.25)

# RELAY_CTRL: R_G Pin 1 (82.0, 32.0) -> (82.0, 30.5) -> (84.0, 30.5) -> (84.0, 60.5) -> (p_u1_1[0], 60.5) -> U1 Pin 1
p_rg_1 = pad_pos(rg, '1'); p_u1_1 = pad_pos(u1, '1')
add_path([p_rg_1, (82.0, 30.5), (84.0, 30.5), (84.0, 60.5), (p_u1_1[0], 60.5), p_u1_1], nets['/RELAY_CTRL'], pcbnew.F_Cu, 0.25)

# ----------------- 3. Power Distribution -----------------
# +5V (F.Cu): U1 Pin 14 (78.38, 59.62) -> X=80.0 north -> Y=38.0
p_u1_14 = pad_pos(u1, '14'); p_d1_1 = pad_pos(d1, '1'); p_ry_1 = pad_pos(ry1, '1'); p_l1_1 = pad_pos(l1, '1')
add_path([p_u1_14, (80.0, p_u1_14[1]), (80.0, 38.0)], nets['+5V'], pcbnew.F_Cu, 0.5)
add_path([(80.0, 38.0), (80.0, p_d1_1[1]), p_d1_1], nets['+5V'], pcbnew.F_Cu, 0.5)
add_path([(80.0, 38.0), (66.0, 38.0), (66.0, p_ry_1[1]), p_ry_1], nets['+5V'], pcbnew.F_Cu, 0.5)
add_path([(66.0, 38.0), (p_l1_1[0], 38.0), p_l1_1], nets['+5V'], pcbnew.F_Cu, 0.5)

# +5V_FILT (F.Cu): L1 Pin 2 (64.16, 35.0) north to (64.16, 32.0) -> west to C7, C6, U2
p_l1_2 = pad_pos(l1, '2'); p_c6_1 = pad_pos(c6, '1'); p_c7_1 = pad_pos(c7, '1'); p_u2_16 = pad_pos(u2, '16')
add_path([p_l1_2, (p_l1_2[0], 32.0), (p_c7_1[0], 32.0), p_c7_1], nets['/+5V_FILT'], pcbnew.F_Cu, 0.5)
# C7 to C6 on F.Cu to avoid crossing COM_L on B.Cu
add_path([p_c7_1, (p_c7_1[0], p_c6_1[1]), p_c6_1], nets['/+5V_FILT'], pcbnew.F_Cu, 0.5)
add_path([p_c7_1, (46.0, 29.5), (37.0, 29.5), (37.0, p_u2_16[1]), p_u2_16], nets['/+5V_FILT'], pcbnew.F_Cu, 0.5)

# +3V3 (B.Cu): U1 Pin 12 to C5; J4 Pin 2 to R1, R2 on B.Cu along X=7.0; J4 Pin 2 to C5 on B.Cu at Y=64.0
p_u1_12 = pad_pos(u1, '12'); p_c5_1 = pad_pos(c5, '1'); p_j4_2 = pad_pos(j4, '2')
p_r1_1 = pad_pos(r1, '1'); p_r2_1 = pad_pos(r2, '1')
add_path([p_u1_12, p_c5_1], nets['+3V3'], pcbnew.F_Cu, 0.4)
add_path([p_c5_1, (70.0, 64.0), (p_j4_2[0], 64.0), p_j4_2], nets['+3V3'], pcbnew.B_Cu, 0.4)
add_path([p_j4_2, (p_j4_2[0], 64.0), (7.0, 64.0), (7.0, p_r1_1[1]), p_r1_1], nets['+3V3'], pcbnew.B_Cu, 0.4)
add_path([(7.0, p_r1_1[1]), (7.0, p_r2_1[1]), p_r2_1], nets['+3V3'], pcbnew.B_Cu, 0.4)

# ----------------- 4. I2C Bus -----------------
# Pullups R2, R1 connect from west directly into U2 Pin 6, 7
p_r2_2 = pad_pos(r2, '2'); p_u2_6 = pad_pos(u2, '6')
add_path([p_r2_2, (p_r2_2[0], p_u2_6[1]), p_u2_6], nets['/I2C_SCL'], pcbnew.F_Cu, 0.2)

p_r1_2 = pad_pos(r1, '2'); p_u2_7 = pad_pos(u2, '7')
add_path([p_r1_2, (p_r1_2[0], p_u2_7[1]), p_u2_7], nets['/I2C_SDA'], pcbnew.F_Cu, 0.2)

# U2 Pin 7 (SDA) routes south via X=30.0; U2 Pin 6 (SCL) routes south via X=32.0 (no crossing!)
p_u1_6 = pad_pos(u1, '6'); p_u1_5 = pad_pos(u1, '5')
add_path([p_u2_7, (30.0, p_u2_7[1]), (30.0, 48.0), (72.5, 48.0)], nets['/I2C_SDA'], pcbnew.F_Cu, 0.2)
add_via(72.5, 48.0, nets['/I2C_SDA'])
add_path([(72.5, 48.0), (72.5, 40.0), (86.0, 40.0)], nets['/I2C_SDA'], pcbnew.B_Cu, 0.2)
add_via(86.0, 40.0, nets['/I2C_SDA'])
add_path([(86.0, 40.0), (96.5, 40.0), (96.5, p_u1_5[1]), p_u1_5], nets['/I2C_SDA'], pcbnew.F_Cu, 0.2)

add_path([p_u2_6, (32.0, p_u2_6[1]), (32.0, 46.5), (74.0, 46.5)], nets['/I2C_SCL'], pcbnew.F_Cu, 0.2)
add_via(74.0, 46.5, nets['/I2C_SCL'])
add_path([(74.0, 46.5), (74.0, 41.5), (86.0, 41.5)], nets['/I2C_SCL'], pcbnew.B_Cu, 0.2)
add_via(86.0, 41.5, nets['/I2C_SCL'])
add_path([(86.0, 41.5), (95.0, 41.5), (95.0, p_u1_6[1]), p_u1_6], nets['/I2C_SCL'], pcbnew.F_Cu, 0.2)

# TOGGLE_SW: J4 Pin 6 north to Y=50.0 -> east to X=76.0 -> north to U1 Pin 9 purely on B.Cu (zero crossings!)
p_j4_6 = pad_pos(j4, '6'); p_u1_9 = pad_pos(u1, '9')
add_path([p_j4_6, (p_j4_6[0], 50.0), (76.0, 50.0), (76.0, p_u1_9[1]), p_u1_9], nets['/TOGGLE_SW'], pcbnew.B_Cu, 0.2)

# LED_SPK: J4 Pin 7 north -> Y=49.46 -> U1 Pin 10
p_j4_7 = pad_pos(j4, '7'); p_u1_10 = pad_pos(u1, '10')
add_path([p_j4_7, (p_j4_7[0], 49.46), p_u1_10], nets['/LED_SPK'], pcbnew.F_Cu, 0.2)

# LED_HP: J4 Pin 8 south -> east to X=29.5 -> north to Y=52.00 -> U1 Pin 11
p_j4_8 = pad_pos(j4, '8'); p_u1_11 = pad_pos(u1, '11')
add_path([p_j4_8, (p_j4_8[0], 59.5), (29.5, 59.5), (29.5, 52.00), p_u1_11], nets['/LED_HP'], pcbnew.F_Cu, 0.2)

# Encoder Bus on South corridor:
# Pin 3 (ENC_A: 16.032, 56.0): south on F.Cu to Y=61.0 -> east along Y=61.0 to X=95.0 -> north to U1 Pin 2 (93.62, 57.08)
p_j4_3 = pad_pos(j4, '3'); p_u1_2 = pad_pos(u1, '2')
add_path([p_j4_3, (p_j4_3[0], 61.0), (95.0, 61.0), (95.0, p_u1_2[1]), p_u1_2], nets['/ENC_A'], pcbnew.F_Cu, 0.2)

# Pin 4 (ENC_B: 17.048, 57.78): south on B.Cu to Y=62.0 -> via to F.Cu -> east along Y=62.0 to X=96.3 -> north to U1 Pin 3 (93.62, 54.54)
p_j4_4 = pad_pos(j4, '4'); p_u1_3 = pad_pos(u1, '3')
add_path([p_j4_4, (p_j4_4[0], 62.0)], nets['/ENC_B'], pcbnew.B_Cu, 0.2)
add_via(p_j4_4[0], 62.0, nets['/ENC_B'])
add_path([(p_j4_4[0], 62.0), (96.3, 62.0), (96.3, p_u1_3[1]), p_u1_3], nets['/ENC_B'], pcbnew.F_Cu, 0.2)

# Pin 5 (ENC_SW: 18.064, 56.0): south on B.Cu to Y=63.0 -> via to F.Cu -> east along Y=63.0 to X=97.6 -> north to U1 Pin 4 (93.62, 52.00)
p_j4_5 = pad_pos(j4, '5'); p_u1_4 = pad_pos(u1, '4')
add_path([p_j4_5, (p_j4_5[0], 63.0)], nets['/ENC_SW'], pcbnew.B_Cu, 0.2)
add_via(p_j4_5[0], 63.0, nets['/ENC_SW'])
add_path([(p_j4_5[0], 63.0), (97.6, 63.0), (97.6, p_u1_4[1]), p_u1_4], nets['/ENC_SW'], pcbnew.F_Cu, 0.2)

# ----------------- 6. Ground Infrastructure -----------------
# Connect J4 Pin 1 (DGND) North to DGND zone
p_j4_1 = pad_pos(j4, '1')
add_path([p_j4_1, (p_j4_1[0], 53.0)], nets['DGND'], pcbnew.B_Cu, 0.3)

# Connect J4 SH2 (DGND) East to DGND zone
add_path([(25.69, 56.89), (28.5, 56.89)], nets['DGND'], pcbnew.B_Cu, 0.3)

# C6 Pad 2 ties to C7 Pad 2 on F.Cu (both east pads, parallel to +5V_FILT, zero crossing!)
# Set C6 Pad 2 zone connection to NONE so it does not starve from isolated pocket on B.Cu
for p in c6.Pads():
    if p.GetNumber() == '2':
        p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_NONE)

p_c6_2 = pad_pos(c6, '2')
p_c7_2 = pad_pos(c7, '2')
add_path([p_c6_2, (p_c7_2[0], p_c6_2[1]), p_c7_2], nets['DGND'], pcbnew.F_Cu, 0.4)

# C7 Pad 2 ties south to DGND zone
add_path([p_c7_2, (p_c7_2[0], 37.0)], nets['DGND'], pcbnew.B_Cu, 0.3)

# U2 DGND pins:
# 1. Pad 17 (35.62, 29.62) connects to Pad 4 (28.00, 29.62) across the IC on F.Cu
# 2. Pad 4 connects to adjacent Pad 5 (28.00, 32.16) on F.Cu
# 3. Pad 17 connects East directly into DGND zone at X=49.0 on B.Cu (zero crossings, zero vias!)
p_u2_4 = pad_pos(u2, '4')
p_u2_5 = pad_pos(u2, '5')
p_u2_17 = pad_pos(u2, '17')
add_path([p_u2_17, p_u2_4], nets['DGND'], pcbnew.F_Cu, 0.3)
add_path([p_u2_4, p_u2_5], nets['DGND'], pcbnew.F_Cu, 0.3)
add_path([p_u2_17, (49.0, p_u2_17[1])], nets['DGND'], pcbnew.B_Cu, 0.3)

# Note: U2 AGND pins (3, 8, 9, 10, 14) are fully covered and connected by the B.Cu AGND plane.


# ----------------- 7. Zones -----------------
zone_agnd = pcbnew.ZONE(board)
zone_agnd.SetLayer(pcbnew.B_Cu)
zone_agnd.SetNetCode(nets['AGND'].GetNetCode())
zone_agnd.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
outline_a = zone_agnd.Outline()
outline_a.NewOutline()
outline_a.Append(mm(0.5), mm(0.5))
outline_a.Append(mm(board_w - 0.5), mm(0.5))
outline_a.Append(mm(board_w - 0.5), mm(17.5))
outline_a.Append(mm(48.0), mm(17.5))
outline_a.Append(mm(48.0), mm(48.0))
outline_a.Append(mm(8.0), mm(48.0))
outline_a.Append(mm(8.0), mm(37.0))
outline_a.Append(mm(0.5), mm(37.0))
board.Add(zone_agnd)

zone_dgnd = pcbnew.ZONE(board)
zone_dgnd.SetLayer(pcbnew.B_Cu)
zone_dgnd.SetNetCode(nets['DGND'].GetNetCode())
zone_dgnd.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
outline_d = zone_dgnd.Outline()
outline_d.NewOutline()
outline_d.Append(mm(0.5), mm(37.0))
outline_d.Append(mm(8.0), mm(37.0))
outline_d.Append(mm(8.0), mm(48.0))
outline_d.Append(mm(48.0), mm(48.0))
outline_d.Append(mm(48.0), mm(17.5))
outline_d.Append(mm(board_w - 0.5), mm(17.5))
outline_d.Append(mm(board_w - 0.5), mm(board_h - 0.5))
outline_d.Append(mm(0.5), mm(board_h - 0.5))
board.Add(zone_dgnd)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard('pcb/main_board/main_board.kicad_pcb', board)
print("Board generated and saved successfully!")
