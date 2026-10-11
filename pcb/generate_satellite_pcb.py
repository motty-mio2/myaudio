import pcbnew
import math

def mm(v):
    return pcbnew.FromMM(v)

board = pcbnew.BOARD()

# Board dimensions: 88mm x 32mm
board_w, board_h = 88.0, 32.0

pts = [
    (0, 0), (board_w, 0),
    (board_w, 0), (board_w, board_h),
    (board_w, board_h), (0, board_h),
    (0, board_h), (0, 0)
]
for i in range(0, len(pts), 2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(pts[i][0], pts[i][1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(pts[i+1][0], pts[i+1][1]))
    seg.SetWidth(mm(0.15))
    board.Add(seg)

# M3 Mounting holes at 4 corners
hole_coords = [(3.5, 3.5), (3.5, 28.5), (84.5, 3.5), (84.5, 28.5)]
for idx, (hx, hy) in enumerate(hole_coords):
    fp_hole = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
    fp_hole.SetReference(f'H{idx+1}')
    fp_hole.Reference().SetVisible(False)
    fp_hole.Value().SetVisible(False)
    fp_hole.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
    board.Add(fp_hole)

# Register nets
net_names = [
    'GND',
    '/ENC_A',
    '/ENC_B',
    '/ENC_SW',
    '/TOGGLE_SW',
    '/LED_SPK',
    '/LED_HP',
    'Net-(LED1-K)',
    'Net-(LED2-K)',
]
nets = {}
for name in net_names:
    net_item = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net_item)
    nets[name] = board.FindNet(name)

def place_fp(pretty_dir, fp_name, ref, val, x, y, rot_deg=0):
    fp = pcbnew.FootprintLoad(f'/usr/share/kicad/footprints/{pretty_dir}.pretty', fp_name)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    board.Add(fp)
    return fp

j1 = place_fp('Connector_RJ', 'RJ45_Amphenol_RJHSE5380', 'J1', 'RJ45_8P8C', 17.0, 16.0, 90)
enc1 = place_fp('Rotary_Encoder', 'RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm', 'ENC1', 'EC11E_Switch', 34.0, 16.0, 0)
led1 = place_fp('LED_THT', 'LED_D3.0mm', 'LED1', 'LED_Green', 56.0, 8.5, 90)
r1 = place_fp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R1', '680', 66.0, 8.5, 0)
led2 = place_fp('LED_THT', 'LED_D3.0mm', 'LED2', 'LED_Blue', 56.0, 23.5, 90)
r2 = place_fp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R2', '680', 66.0, 23.5, 0)
sw1 = place_fp('Button_Switch_THT', 'SW_PUSH_6mm', 'SW1', 'SW_Push', 76.0, 16.0, 0)

# Pad net assignments
j1_pads = {
    '1': nets['GND'],
    '3': nets['/ENC_A'],
    '4': nets['/ENC_B'],
    '5': nets['/ENC_SW'],
    '6': nets['/TOGGLE_SW'],
    '7': nets['/LED_SPK'],
    '8': nets['/LED_HP'],
    'SH': nets['GND'],
}
for p in j1.Pads():
    num = p.GetNumber()
    if num in j1_pads:
        p.SetNet(j1_pads[num])

enc1_pads = {
    'A': nets['/ENC_A'],
    'B': nets['/ENC_B'],
    'C': nets['GND'],
    'S1': nets['/ENC_SW'],
    'S2': nets['GND'],
    'MP': nets['GND'],
}
for p in enc1.Pads():
    num = p.GetNumber()
    if num in enc1_pads:
        p.SetNet(enc1_pads[num])

for p in sw1.Pads():
    num = p.GetNumber()
    if num == '1':
        p.SetNet(nets['/TOGGLE_SW'])
    elif num == '2':
        p.SetNet(nets['GND'])

for p in led1.Pads():
    num = p.GetNumber()
    if num == '2':
        p.SetNet(nets['/LED_SPK'])
    elif num == '1':
        p.SetNet(nets['Net-(LED1-K)'])

for p in r1.Pads():
    num = p.GetNumber()
    if num == '1':
        p.SetNet(nets['Net-(LED1-K)'])
    elif num == '2':
        p.SetNet(nets['GND'])

for p in led2.Pads():
    num = p.GetNumber()
    if num == '2':
        p.SetNet(nets['/LED_HP'])
    elif num == '1':
        p.SetNet(nets['Net-(LED2-K)'])

for p in r2.Pads():
    num = p.GetNumber()
    if num == '1':
        p.SetNet(nets['Net-(LED2-K)'])
    elif num == '2':
        p.SetNet(nets['GND'])

def pad_pos(fp, pad_num):
    for p in fp.Pads():
        if p.GetNumber() == pad_num:
            pos = p.GetPosition()
            return round(pcbnew.ToMM(pos.x), 2), round(pcbnew.ToMM(pos.y), 2)
    raise ValueError(f"Pad {pad_num} not found on {fp.GetReference()}")

def all_pad_positions(fp, pad_num):
    positions = []
    for p in fp.Pads():
        if p.GetNumber() == pad_num:
            pos = p.GetPosition()
            positions.append((round(pcbnew.ToMM(pos.x), 2), round(pcbnew.ToMM(pos.y), 2)))
    return positions

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
        add_track(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net, layer, width_mm)

# Connect pairs of pads on SW1
sw_pads_1 = all_pad_positions(sw1, '1')
if len(sw_pads_1) >= 2:
    add_path([sw_pads_1[0], sw_pads_1[1]], nets['/TOGGLE_SW'])
sw_pads_2 = all_pad_positions(sw1, '2')
if len(sw_pads_2) >= 2:
    add_path([sw_pads_2[0], sw_pads_2[1]], nets['GND'], pcbnew.B_Cu)

# Pad positions on J1:
p_j8 = pad_pos(j1, '8') # (18.78, 8.89)
p_j7 = pad_pos(j1, '7') # (17.00, 9.90)
p_j6 = pad_pos(j1, '6') # (18.78, 10.92)
p_j5 = pad_pos(j1, '5') # (17.00, 11.94)
p_j4 = pad_pos(j1, '4') # (18.78, 12.95)
p_j3 = pad_pos(j1, '3') # (17.00, 13.97)

# --- EVEN PADS (Route East) ---
# 1. /LED_HP: Pin 8 -> East -> B.Cu loop to LED2 pin 2 (56.0, 20.96)
p_l2_2 = pad_pos(led2, '2')
add_path([p_j8, (21.5, p_j8[1]), (21.5, 2.5), (51.0, 2.5), (53.0, p_l2_2[1]), p_l2_2], nets['/LED_HP'], pcbnew.B_Cu)

# 2. /TOGGLE_SW: Pin 6 -> East -> F.Cu to SW1 pad 1
p_sw1_1 = sw_pads_1[0]
add_path([p_j6, (23.5, p_j6[1]), (23.5, 5.5), (50.0, 5.5), (52.0, 13.5), (71.0, 13.5), p_sw1_1], nets['/TOGGLE_SW'])

# 3. /ENC_B: Pin 4 -> East -> F.Cu to ENC1 pad B
p_eb = pad_pos(enc1, 'B')
add_path([p_j4, (27.5, p_j4[1]), (27.5, p_eb[1]), p_eb], nets['/ENC_B'])

# --- ODD PADS (Route West, perfectly parallel) ---
# 4. /LED_SPK: Pin 7 -> West to x=10.0 -> North to y=2.0 -> East to LED1 pin 2
p_l1_2 = pad_pos(led1, '2')
add_path([p_j7, (10.0, p_j7[1]), (10.0, 2.0), (51.0, 2.0), (53.0, p_l1_2[1]), p_l1_2], nets['/LED_SPK'])

# 5. /ENC_SW: Pin 5 -> West to x=7.0 -> South to y=27.0 -> East to ENC1 pad S1
p_es1 = pad_pos(enc1, 'S1')
add_path([p_j5, (7.0, p_j5[1]), (7.0, 27.0), (46.0, 27.0), (46.0, p_es1[1]), p_es1], nets['/ENC_SW'])

# 6. /ENC_A: Pin 3 -> West to x=8.5 -> South to y=28.5 -> East on B.Cu to ENC1 pad A
p_ea = pad_pos(enc1, 'A')
add_path([p_j3, (8.5, p_j3[1]), (8.5, 28.5), (28.0, 28.5), (28.0, p_ea[1]), p_ea], nets['/ENC_A'], pcbnew.B_Cu)

# 7. Net-(LED1-K): LED1 pin 1 to R1 pin 1
p_l1_1 = pad_pos(led1, '1')
p_r1_1 = pad_pos(r1, '1')
add_path([p_l1_1, (60.0, p_l1_1[1]), (61.0, p_r1_1[1]), p_r1_1], nets['Net-(LED1-K)'])

# 8. Net-(LED2-K): LED2 pin 1 to R2 pin 1
p_l2_1 = pad_pos(led2, '1')
p_r2_1 = pad_pos(r2, '1')
add_path([p_l2_1, (60.0, p_l2_1[1]), (61.0, p_r2_1[1]), p_r2_1], nets['Net-(LED2-K)'])

# Add B.Cu GND Copper Zone (Fill Zone)
zone = pcbnew.ZONE(board)
zone.SetLayer(pcbnew.B_Cu)
zone.SetNetCode(nets['GND'].GetNetCode())
outline = zone.Outline()
outline.NewOutline()
outline.Append(mm(0.5), mm(0.5))
outline.Append(mm(board_w - 0.5), mm(0.5))
outline.Append(mm(board_w - 0.5), mm(board_h - 0.5))
outline.Append(mm(0.5), mm(board_h - 0.5))
board.Add(zone)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# Silkscreen text
def add_silk_text(board, text, x, y, rot=0, size_mm=1.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    t.SetTextSize(pcbnew.VECTOR2I_MM(size_mm, size_mm))
    t.SetTextThickness(mm(0.15))
    t.SetTextAngle(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    board.Add(t)

add_silk_text(board, "SATELLITE v1.0", 42.0, 3.5, 0, 1.2)
add_silk_text(board, "SPK", 56.0, 4.0, 0, 0.9)
add_silk_text(board, "HP", 56.0, 28.0, 0, 0.9)
add_silk_text(board, "SEL", 76.0, 10.5, 0, 0.9)
add_silk_text(board, "VOL / MUTE", 34.0, 28.0, 0, 0.9)

pcbnew.SaveBoard('pcb/satellite/satellite.kicad_pcb', board)
print("satellite.kicad_pcb cleanly generated and zone filled!")
