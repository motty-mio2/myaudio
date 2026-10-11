import pcbnew
import math
import heapq
import re
from collections import defaultdict

def mm(v):
    return pcbnew.FromMM(v)

board = pcbnew.BOARD()
board_w, board_h = 100.0, 70.0

# ----------------- Edge Cuts (100x70 rectangle) -----------------
pts = [(0, 0), (board_w, 0), (board_w, board_h), (0, board_h)]
for i in range(4):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(pts[i][0], pts[i][1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(pts[(i+1)%4][0], pts[(i+1)%4][1]))
    seg.SetWidth(mm(0.15))
    board.Add(seg)

# ----------------- M3 Mounting Holes -----------------
hole_coords = [(4.0, 4.0), (4.0, board_h - 4.0), (board_w - 4.0, 4.0), (board_w - 4.0, board_h - 4.0)]
for idx, (hx, hy) in enumerate(hole_coords):
    fp_hole = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3')
    fp_hole.SetReference(f'H{idx+1}')
    fp_hole.Reference().SetVisible(False)
    fp_hole.Value().SetVisible(False)
    fp_hole.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
    board.Add(fp_hole)

# ----------------- Parse Netlist -----------------
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
        ref, pin = pm.group(1), pm.group(2)
        pins.append((ref, pin))
    net_pins[name] = pins

def place_fp(pretty_path, fp_name, ref, val, x, y, rot_deg=0):
    fp = pcbnew.FootprintLoad(pretty_path, fp_name)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.Value().SetVisible(False)
    fp.Reference().SetVisible(False)
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    board.Add(fp)
    return fp

# ----------------- Component Placement -----------------
# Audio Jacks (North Edge Y=10.0, Facing Up)
j1 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J1', 'Line_In', 15.0, 10.0, 180)
j2 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J2', 'Speaker_Out', 53.0, 10.0, 180)
j3 = place_fp('pcb/main_board/main_board_footprints.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal', 'J3', 'Headphone_Out', 82.0, 10.0, 180)

# Input Capacitors
c1 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C1', '4.7uF', 14.0, 22.0, 0)
c2 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C2', '4.7uF', 22.0, 22.0, 0)

# PT2258 Volume Control IC (DIP-20)
u2 = place_fp('/usr/share/kicad/footprints/Package_DIP.pretty', 'DIP-20_W7.62mm', 'U2', 'PT2258', 28.0, 22.0, 0)

# Output Capacitors, REF Capacitor & LC Filter
c4 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C4', '4.7uF', 43.0, 20.0, 0)
c3 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C3', '4.7uF', 43.0, 26.0, 0)
c8 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D5.0mm_P2.50mm', 'C8', '10uF', 43.0, 32.0, 0)

c6 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'CP_Radial_D6.3mm_P2.50mm', 'C6', '100uF', 51.0, 20.0, 0)
c7 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'C_Disc_D4.3mm_W1.9mm_P5.00mm', 'C7', '0.1uF', 51.0, 26.0, 0)
l1 = place_fp('/usr/share/kicad/footprints/Inductor_THT.pretty', 'L_Axial_L7.0mm_D3.3mm_P10.16mm_Horizontal_Fastron_MICC', 'L1', '10uH', 48.0, 32.0, 0)

# Relay RY1 (Omron G6K-2P-Y, Rot 90)
ry1 = place_fp('/usr/share/kicad/footprints/Relay_THT.pretty', 'Relay_DPDT_Omron_G6K-2P-Y', 'RY1', 'G6K-2P-Y_DC5', 64.0, 25.0, 90)

# Relay Driver Block
d1 = place_fp('/usr/share/kicad/footprints/Diode_THT.pretty', 'D_DO-35_SOD27_P7.62mm_Horizontal', 'D1', '1N4148', 76.0, 20.0, 0)
q1 = place_fp('/usr/share/kicad/footprints/Package_TO_SOT_THT.pretty', 'TO-92_Inline', 'Q1', '2N7000', 76.0, 27.0, 0)
rg = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R_G', '1k', 76.0, 33.0, 0)
r3 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R3', '10k', 64.0, 33.0, 0)

# I2C Pull-ups (West of U2)
r2 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R2', '4.7k', 12.0, 37.0, 0)
r1 = place_fp('/usr/share/kicad/footprints/Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 'R1', '4.7k', 12.0, 42.0, 0)

# Star Ground Tie
nt1 = place_fp('/usr/share/kicad/footprints/NetTie.pretty', 'NetTie-2_THT_Pad1.0mm', 'NT1', 'NetTie_2', 4.0, 36.0, 0)

# RJ45 Satellite Connector (South-West)
j4 = place_fp('/usr/share/kicad/footprints/Connector_RJ.pretty', 'RJ45_Amphenol_RJHSE5380', 'J4', 'RJ45_Satellite', 14.0, 56.0, 0)

# XIAO ESP32-C6 Socket (South-East)
u1 = place_fp('pcb/main_board/main_board_footprints.pretty', 'XIAO_ESP32C6_Socket', 'U1', 'XIAO_ESP32C6', 86.0, 52.0, 180)

# XIAO Decoupling Cap
c5 = place_fp('/usr/share/kicad/footprints/Capacitor_THT.pretty', 'C_Disc_D4.3mm_W1.9mm_P5.00mm', 'C5', '0.1uF', 70.0, 54.54, 0)

fp_by_ref = {
    'J1': j1, 'J2': j2, 'J3': j3, 'J4': j4, 'U1': u1, 'U2': u2,
    'RY1': ry1, 'C1': c1, 'C2': c2, 'C3': c3, 'C4': c4, 'C8': c8,
    'Q1': q1, 'D1': d1, 'R_G': rg, 'R3': r3,
    'L1': l1, 'C6': c6, 'C7': c7, 'C5': c5, 'R1': r1, 'R2': r2,
    'NT1': nt1
}

for net_name, pins in net_pins.items():
    if net_name not in nets:
        continue
    net_obj = nets[net_name]
    for ref, pin_num in pins:
        if ref in fp_by_ref:
            fp = fp_by_ref[ref]
            for pad in fp.Pads():
                if pad.GetNumber() == pin_num:
                    pad.SetNet(net_obj)

for pad in j4.Pads():
    if pad.GetNumber() == 'SH':
        pad.SetNet(nets['DGND'])

# ----------------- A* Grid Router -----------------
GRID_RES = 0.5  # 0.5mm resolution
grid_w = int(board_w / GRID_RES) + 1
grid_h = int(board_h / GRID_RES) + 1

# Grid: 0 = F.Cu, 1 = B.Cu. Values: None or net_code
grid = [{}, {}]

# Populate Pad Obstacles
pad_positions = {}
all_pads = []
for fp in board.GetFootprints():
    for pad in fp.Pads():
        pos = pad.GetPosition()
        x_mm = round(pos.x / 1e6, 3)
        y_mm = round(pos.y / 1e6, 3)
        net_code = pad.GetNetCode()
        ref = fp.GetReference()
        num = pad.GetNumber()
        pad_positions[(ref, num)] = (x_mm, y_mm, net_code)
        is_npth = (pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
        all_pads.append((x_mm, y_mm, net_code, is_npth))

# Mark initial obstacles in grid
for x_mm, y_mm, net_code, is_npth in all_pads:
    # Radius of obstacle
    r_mm = 1.6 if is_npth else 0.8
    r_cells = int(math.ceil(r_mm / GRID_RES))
    cx = int(round(x_mm / GRID_RES))
    cy = int(round(y_mm / GRID_RES))
    for dx in range(-r_cells, r_cells + 1):
        for dy in range(-r_cells, r_cells + 1):
            if math.hypot(dx * GRID_RES, dy * GRID_RES) <= r_mm:
                gx, gy = cx + dx, cy + dy
                if 0 <= gx < grid_w and 0 <= gy < grid_h:
                    grid[0][(gx, gy)] = (net_code if not is_npth else -1)
                    grid[1][(gx, gy)] = (net_code if not is_npth else -1)

# Mounting holes
for hx, hy in hole_coords:
    cx = int(round(hx / GRID_RES))
    cy = int(round(hy / GRID_RES))
    r_cells = int(math.ceil(2.0 / GRID_RES))
    for dx in range(-r_cells, r_cells + 1):
        for dy in range(-r_cells, r_cells + 1):
            if math.hypot(dx * GRID_RES, dy * GRID_RES) <= 2.0:
                gx, gy = cx + dx, cy + dy
                grid[0][(gx, gy)] = -1
                grid[1][(gx, gy)] = -1

# Edge margin (1mm from edge)
edge_margin = int(1.0 / GRID_RES)
for x in range(grid_w):
    for y in range(edge_margin):
        grid[0][(x, y)] = -1
        grid[1][(x, y)] = -1
        grid[0][(x, grid_h - 1 - y)] = -1
        grid[1][(x, grid_h - 1 - y)] = -1
for y in range(grid_h):
    for x in range(edge_margin):
        grid[0][(x, y)] = -1
        grid[1][(x, y)] = -1
        grid[0][(grid_w - 1 - x, y)] = -1
        grid[1][(grid_w - 1 - x, y)] = -1

def astar_route(start_pos, end_pos, net_code, preferred_layer=0):
    sx = int(round(start_pos[0] / GRID_RES))
    sy = int(round(start_pos[1] / GRID_RES))
    ex = int(round(end_pos[0] / GRID_RES))
    ey = int(round(end_pos[1] / GRID_RES))

    # Priority queue: (f_score, cost, (x, y, layer), path)
    h_start = math.hypot(sx - ex, sy - ey)
    pq = [(h_start, 0, (sx, sy, preferred_layer), [(sx, sy, preferred_layer)])]
    visited = {}

    target_cells = set()
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            target_cells.add((ex + dx, ey + dy))

    while pq:
        f, cost, (x, y, l), path = heapq.heappop(pq)

        if (x, y) == (ex, ey) or ((x, y) in target_cells and len(path) > 3):
            # Target reached!
            final_path = path
            if (x, y) != (ex, ey):
                final_path.append((ex, ey, l))
            return final_path

        state = (x, y, l)
        if state in visited and visited[state] <= cost:
            continue
        visited[state] = cost

        # Neighbors: 4 directions + layer change
        moves = [
            (x + 1, y, l, 1.0),
            (x - 1, y, l, 1.0),
            (x, y + 1, l, 1.0),
            (x, y - 1, l, 1.0),
            (x, y, 1 - l, 8.0)  # Via penalty
        ]

        for nx, ny, nl, move_cost in moves:
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                continue
            
            # Check collision
            occ = grid[nl].get((nx, ny), None)
            if occ is not None and occ != net_code:
                # Blocked by another net or obstacle
                # Exception: if (nx, ny) is the exact target pad
                if not (nx == ex and ny == ey):
                    continue

            # Layer preference penalty
            layer_pen = 0.2 if nl != preferred_layer else 0.0
            new_cost = cost + move_cost + layer_pen
            h = math.hypot(nx - ex, ny - ey)
            nstate = (nx, ny, nl)
            if nstate not in visited or visited[nstate] > new_cost:
                heapq.heappush(pq, (new_cost + h, new_cost, nstate, path + [nstate]))

    return None

def commit_path(path, net_code, net_obj, width_mm=0.25):
    if not path:
        return
    # Mark grid cells occupied
    for x, y, l in path:
        # Mark 0.5mm around track
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                gx, gy = x + dx, y + dy
                grid[l][(gx, gy)] = net_code

    # Simplify collinear segments
    points_by_layer = []
    current_seg = [path[0]]
    for i in range(1, len(path)):
        prev = path[i-1]
        curr = path[i]
        if curr[2] != prev[2]:
            # Via occurred
            points_by_layer.append((prev[2], current_seg))
            # Add via
            vx, vy = curr[0] * GRID_RES, curr[1] * GRID_RES
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I_MM(vx, vy))
            via.SetWidth(mm(0.8))
            via.SetDrill(mm(0.4))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(net_obj)
            board.Add(via)
            current_seg = [curr]
        else:
            current_seg.append(curr)
    points_by_layer.append((path[-1][2], current_seg))

    # Add tracks
    for layer_idx, seg in points_by_layer:
        layer = pcbnew.F_Cu if layer_idx == 0 else pcbnew.B_Cu
        # Coalesce collinear
        if len(seg) < 2:
            continue
        cleaned = [seg[0]]
        for i in range(1, len(seg) - 1):
            p_prev = seg[i-1]
            p_curr = seg[i]
            p_next = seg[i+1]
            dx1 = p_curr[0] - p_prev[0]
            dy1 = p_curr[1] - p_prev[1]
            dx2 = p_next[0] - p_curr[0]
            dy2 = p_next[1] - p_curr[1]
            if (dx1 == dx2 and dy1 == dy2):
                continue
            cleaned.append(p_curr)
        cleaned.append(seg[-1])

        for i in range(len(cleaned) - 1):
            x1, y1 = cleaned[i][0] * GRID_RES, cleaned[i][1] * GRID_RES
            x2, y2 = cleaned[i+1][0] * GRID_RES, cleaned[i+1][1] * GRID_RES
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
            t.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
            t.SetWidth(mm(width_mm))
            t.SetLayer(layer)
            t.SetNet(net_obj)
            board.Add(t)

# Route list in order of priority:
route_list = [
    # Audio
    ('/LINE_IN_L', ('J1', 'T'), ('C1', '1'), 0, 0.3),
    ('/LINE_IN_R', ('J1', 'R'), ('C2', '1'), 0, 0.3),
    ('/VOL_IN_L', ('C1', '2'), ('U2', '1'), 1, 0.3),
    ('/VOL_IN_R', ('C2', '2'), ('U2', '2'), 0, 0.3),
    ('Net-(U2-REF)', ('U2', '15'), ('C8', '1'), 0, 0.3),
    ('/VOL_OUT_L', ('U2', '20'), ('C3', '1'), 1, 0.3),
    ('/VOL_OUT_R', ('U2', '19'), ('C4', '1'), 0, 0.3),
    ('/COM_L', ('C3', '2'), ('RY1', '3'), 0, 0.3),
    ('/COM_R', ('C4', '2'), ('RY1', '6'), 0, 0.3),
    ('/SPK_OUT_L', ('RY1', '2'), ('J2', 'T'), 1, 0.3),
    ('/SPK_OUT_R', ('RY1', '7'), ('J2', 'R'), 0, 0.3),
    ('/HP_OUT_L', ('RY1', '4'), ('J3', 'T'), 1, 0.3),
    ('/HP_OUT_R', ('RY1', '5'), ('J3', 'R'), 0, 0.3),

    # Relay driver
    ('/RELAY_COIL_NEG', ('RY1', '8'), ('D1', '2'), 1, 0.3),
    ('/RELAY_COIL_NEG', ('D1', '2'), ('Q1', '3'), 1, 0.3),
    ('Net-(Q1-G)', ('Q1', '2'), ('R_G', '2'), 0, 0.25),
    ('Net-(Q1-G)', ('R_G', '2'), ('R3', '1'), 0, 0.25),
    ('/RELAY_CTRL', ('R_G', '1'), ('U1', '1'), 1, 0.25),

    # Power
    ('+5V', ('U1', '14'), ('D1', '1'), 0, 0.5),
    ('+5V', ('D1', '1'), ('RY1', '1'), 0, 0.5),
    ('+5V', ('D1', '1'), ('L1', '1'), 0, 0.5),
    ('/+5V_FILT', ('L1', '2'), ('C6', '1'), 0, 0.5),
    ('/+5V_FILT', ('C6', '1'), ('C7', '1'), 0, 0.5),
    ('/+5V_FILT', ('C7', '1'), ('U2', '16'), 0, 0.5),
    ('+3V3', ('U1', '12'), ('C5', '1'), 0, 0.4),
    ('+3V3', ('C5', '1'), ('J4', '2'), 0, 0.4),
    ('+3V3', ('J4', '2'), ('R1', '1'), 0, 0.4),
    ('+3V3', ('R1', '1'), ('R2', '1'), 0, 0.4),

    # I2C
    ('/I2C_SCL', ('U1', '6'), ('R2', '2'), 0, 0.25),
    ('/I2C_SCL', ('R2', '2'), ('U2', '6'), 0, 0.25),
    ('/I2C_SDA', ('U1', '5'), ('R1', '2'), 0, 0.25),
    ('/I2C_SDA', ('R1', '2'), ('U2', '7'), 0, 0.25),

    # Satellite
    ('/TOGGLE_SW', ('J4', '6'), ('U1', '9'), 0, 0.25),
    ('/LED_SPK', ('J4', '7'), ('U1', '10'), 0, 0.25),
    ('/LED_HP', ('J4', '8'), ('U1', '11'), 0, 0.25),
    ('/ENC_SW', ('J4', '5'), ('U1', '4'), 0, 0.25),
    ('/ENC_B', ('J4', '4'), ('U1', '3'), 0, 0.25),
    ('/ENC_A', ('J4', '3'), ('U1', '2'), 0, 0.25),

    # Ground escapes into plane
    ('DGND', ('U2', '4'), ('NT1', '2'), 1, 0.3),
    ('DGND', ('U2', '5'), ('U2', '4'), 1, 0.3),
    ('DGND', ('U2', '17'), ('U2', '4'), 1, 0.3),
    ('DGND', ('Q1', '1'), ('NT1', '2'), 1, 0.3),
    ('DGND', ('R3', '2'), ('Q1', '1'), 1, 0.3),
    ('DGND', ('C6', '2'), ('NT1', '2'), 1, 0.3),
    ('DGND', ('C7', '2'), ('C6', '2'), 1, 0.3),

    ('AGND', ('U2', '3'), ('U2', '8'), 1, 0.3),
    ('AGND', ('U2', '8'), ('U2', '9'), 1, 0.3),
    ('AGND', ('U2', '9'), ('U2', '10'), 1, 0.3),
    ('AGND', ('U2', '14'), ('C8', '2'), 1, 0.3),
    ('AGND', ('C8', '2'), ('NT1', '1'), 1, 0.3),
]

print(f"Routing {len(route_list)} connections using A* maze router...")
for net_name, p1_info, p2_info, pref_layer, width in route_list:
    p1 = pad_positions[p1_info]
    p2 = pad_positions[p2_info]
    net_obj = nets[net_name]
    net_code = net_obj.GetNetCode()

    path = astar_route((p1[0], p1[1]), (p2[0], p2[1]), net_code, pref_layer)
    if path:
        commit_path(path, net_code, net_obj, width)
        print(f"  [OK] {net_name} ({p1_info[0]}:{p1_info[1]} -> {p2_info[0]}:{p2_info[1]}), steps: {len(path)}")
    else:
        print(f"  [FAIL] Could not route {net_name} ({p1_info[0]}:{p1_info[1]} -> {p2_info[0]}:{p2_info[1]})")

# ----------------- Ground Zones -----------------
# AGND Zone on B.Cu (Upper board Y: 0.5 to 36.0)
zone_agnd = pcbnew.ZONE(board)
zone_agnd.SetLayer(pcbnew.B_Cu)
zone_agnd.SetNetCode(nets['AGND'].GetNetCode())
zone_agnd.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
outline_a = zone_agnd.Outline()
outline_a.NewOutline()
outline_a.Append(mm(0.5), mm(0.5))
outline_a.Append(mm(board_w - 0.5), mm(0.5))
outline_a.Append(mm(board_w - 0.5), mm(36.0))
outline_a.Append(mm(0.5), mm(36.0))
board.Add(zone_agnd)

# DGND Zone on B.Cu (Lower board Y: 36.0 to 69.5)
zone_dgnd = pcbnew.ZONE(board)
zone_dgnd.SetLayer(pcbnew.B_Cu)
zone_dgnd.SetNetCode(nets['DGND'].GetNetCode())
zone_dgnd.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
outline_d = zone_dgnd.Outline()
outline_d.NewOutline()
outline_d.Append(mm(0.5), mm(36.0))
outline_d.Append(mm(board_w - 0.5), mm(36.0))
outline_d.Append(mm(board_w - 0.5), mm(board_h - 0.5))
outline_d.Append(mm(0.5), mm(board_h - 0.5))
board.Add(zone_dgnd)

# Fill Zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard('pcb/main_board/main_board.kicad_pcb', board)
print("Complete main_board.kicad_pcb cleanly generated and zone filled!")
