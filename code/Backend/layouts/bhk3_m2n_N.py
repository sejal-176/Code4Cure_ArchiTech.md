def generate(plot_height: int, plot_width: int) -> dict:
    import uuid
    from datetime import datetime
    from ortools.sat.python import cp_model
    import math
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Arc, Circle, Ellipse
    from dataclasses import dataclass
    import numpy as np
    import matplotlib
    matplotlib.use('Agg') 

    layout_id = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    PLOT_WIDTH = plot_width
    PLOT_HEIGHT = plot_height
    PLOT_AREA = PLOT_WIDTH * PLOT_HEIGHT

    rooms = {
        "Living": (18, 22),              # ~460
        "Kitchen_Balcony": (3, 4),        # ~80
        "Kitchen": (12, 14),             # ~250
        "Normal1_Bedroom": (10, 14),      # ~230
        "Normal2_Bedroom": (9, 11),       # ~240
        "Master_Bedroom": (11, 13),      # ~300
        "Master_Toilet": (3, 5),         # ~100
        "Common_Toilet": (2, 4),          # ~40
        "Bathroom": (2, 4),             # ~70
        "corridor": (6, 10)
    }

    model = cp_model.CpModel()
    area_vars = {}

    for room, (min_p, max_p) in rooms.items():
        min_area = int(PLOT_AREA * min_p / 100)
        max_area = int(PLOT_AREA * max_p / 100)
        area_vars[room] = model.NewIntVar(min_area, max_area, f"{room}_area")

    model.Add(sum(area_vars.values()) == PLOT_AREA)
    model.Maximize(sum(area_vars.values()))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No feasible solution found.")

    rooms = {room: solver.Value(var) for room, var in area_vars.items()}

    #data structures
    @dataclass
    class Point:
        x: float
        y: float

    @dataclass
    class Room:
        a1: Point
        a2: Point
        a3: Point
        a4: Point
        area: float

    #layout logic
    WALL_THICKNESS = 0.5
    layout = {}

    #master bedroom + master toilet
    mb_h = PLOT_HEIGHT * 0.35
    mb_w = (rooms["Master_Bedroom"] + rooms["Master_Toilet"]) / mb_h
    layout["Master_Bedroom"] = Room(Point(0, mb_h), Point(mb_w, mb_h), Point(mb_w, 0), Point(0, 0), rooms["Master_Bedroom"])

    mt_w = math.sqrt(rooms["Master_Toilet"] * 1.2)
    mt_h = rooms["Master_Toilet"] / mb_w
    layout["Master_Toilet"] = Room(Point(0, mb_h), Point(mt_w, mb_h), Point(mt_w, mb_h - mt_h), Point(0, mb_h - mt_h), rooms["Master_Toilet"])

    #kitchen+balcony
    kit_w = PLOT_WIDTH - mb_w
    kit_h = (rooms["Kitchen"]+ rooms["Kitchen_Balcony"]) / kit_w
    layout["Kitchen"] = Room(Point(PLOT_WIDTH - kit_w, kit_h), Point(PLOT_WIDTH, kit_h), Point(PLOT_WIDTH, 0), Point(PLOT_WIDTH - kit_w, 0), rooms["Kitchen"])

    bal_h = kit_h
    bal_w = rooms["Kitchen_Balcony"] / bal_h
    layout["Kitchen_Balcony"] = Room(Point(PLOT_WIDTH - bal_w, bal_h), Point(PLOT_WIDTH, bal_h), Point(PLOT_WIDTH, 0), Point(PLOT_WIDTH - bal_w, 0), rooms["Kitchen_Balcony"])

    #living
    living_h = PLOT_HEIGHT - kit_h
    living_w = (rooms["Living"] ) / living_h
    layout["Living"] = Room(Point(PLOT_WIDTH - living_w, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT - living_h), Point(PLOT_WIDTH - living_w, PLOT_HEIGHT - living_h), rooms["Living"])

    #guest bedroom + normal bedroom
    mid_tw = PLOT_WIDTH - living_w
    guest_w = mid_tw * 0.4
    guest_h = rooms["Normal2_Bedroom"] / guest_w
    layout["Normal2_Bedroom"] = Room(Point(PLOT_WIDTH - living_w - guest_w, PLOT_HEIGHT), Point(PLOT_WIDTH - living_w, PLOT_HEIGHT), Point(PLOT_WIDTH - living_w, PLOT_HEIGHT - guest_h), Point(PLOT_WIDTH - living_w - guest_w, PLOT_HEIGHT - guest_h), rooms["Normal2_Bedroom"])

    nb_w = PLOT_WIDTH - living_w - guest_w
    nb_h = rooms["Normal1_Bedroom"] / nb_w

    #bathroom + common toilet
    up_remain_height = PLOT_HEIGHT - nb_h - mb_h
    bath_h = up_remain_height * 0.5
    bath_w = rooms["Bathroom"] / bath_h

    layout["Normal1_Bedroom"] = Room(Point(0, PLOT_HEIGHT), Point(nb_w, PLOT_HEIGHT), Point(nb_w, PLOT_HEIGHT - nb_h), Point(0, PLOT_HEIGHT - nb_h), rooms["Normal1_Bedroom"])
    layout["Bathroom"] = Room(Point(0, mb_h + bath_h), Point(bath_w, mb_h + bath_h), Point(bath_w, mb_h), Point(0, mb_h), rooms["Bathroom"])

    toilet_h = up_remain_height - bath_h
    toilet_w = rooms["Common_Toilet"] / toilet_h
    layout["Common_Toilet"] = Room(Point(0, PLOT_HEIGHT - nb_h), Point(toilet_w, PLOT_HEIGHT - nb_h), Point(toilet_w, PLOT_HEIGHT - nb_h - toilet_h), Point(0, PLOT_HEIGHT - nb_h - toilet_h), rooms["Common_Toilet"])

    #furniture drawing logic
    def draw_furniture(ax, room_name, room):
        fabric_color = '#94a3b8'
        detail_color = '#475569'
        wood_color = '#b5835a'

        if room_name == "Living":
            if PLOT_WIDTH > PLOT_HEIGHT:
                ax.add_patch(Rectangle((PLOT_WIDTH-kit_w*0.5, room.a3.y + WALL_THICKNESS),kit_w*0.5-WALL_THICKNESS, living_h*0.15, color=fabric_color, ec=detail_color, lw=1, zorder=20))#horizontal-sofa
                for i in range(int(kit_w*0.5/(living_h*0.1))-2):
                    ax.add_patch(Rectangle((PLOT_WIDTH-kit_w*0.5 + 0.5 + (i*(living_h*0.2)), room.a3.y + WALL_THICKNESS), living_h*0.12, living_h*0.07, fill=False, ec=detail_color, lw=0.5, zorder=21))#cushion
            else:
                ax.add_patch(Rectangle((PLOT_WIDTH-living_w*0.8, room.a3.y + WALL_THICKNESS),living_w*0.8-WALL_THICKNESS, living_h*0.15, color=fabric_color, ec=detail_color, lw=1, zorder=20))#horizontal-sofa
                for i in range(int(living_w*0.8/(living_h*0.15))-1):
                    ax.add_patch(Rectangle((PLOT_WIDTH-living_w*0.8 + 0.5 + (i*(living_h*0.2)), room.a3.y + WALL_THICKNESS), living_h*0.15, living_h*0.07, fill=False, ec=detail_color, lw=0.5, zorder=21))#cushion
            
            ax.add_patch(Rectangle((room.a3.x - WALL_THICKNESS-min(living_w*0.2,living_h*0.15), room.a3.y + WALL_THICKNESS), min(living_h*0.15,living_w*0.2), living_h*0.4, color=fabric_color, ec=detail_color, lw=1, zorder=20))#vertical-sofa
            tx, ty = room.a4.x + (room.a2.x - room.a1.x)/2 - 3.0, room.a4.y + (room.a1.y - room.a4.y)/2 - 2.0
            ax.add_patch(Rectangle((tx, ty), living_w*0.4, living_h*0.15, facecolor=wood_color, edgecolor='#5c4033', lw=1.5, zorder=22))
            ax.add_patch(Rectangle((PLOT_WIDTH-living_w*0.85, (PLOT_HEIGHT-living_h*0.06-WALL_THICKNESS)), living_w*0.4, living_h*0.06, color=wood_color, ec=detail_color, zorder=20)) #tv

        elif room_name == "Kitchen":
           
            ax.add_patch(Rectangle((room.a2.x - bal_w*1.6 -WALL_THICKNESS, room.a3.y+bal_h*0.15), (kit_w*0.15), (room.a2.y - (room.a3.y)-WALL_THICKNESS-bal_h*0.15), color='#e2e8f0', ec='#94a3b8', zorder=20))#kitchen edge
            stove_x, stove_y = room.a2.x - bal_w*1.4-WALL_THICKNESS, room.a4.y + (room.a1.y - room.a4.y) / 2 - 1.5
            ax.add_patch(Rectangle((stove_x, stove_y), kit_w*0.08, kit_h*0.3, color='#334155', zorder=21))
            for i in range(3):
              ax.add_patch(Circle((stove_x + kit_w*0.05, stove_y + kit_h*0.04+ i*(kit_h*0.25/3)), kit_h*0.025, color='black', ec='white', lw=0.3, zorder=22))
            
            t_width, t_height = kit_w*0.3, kit_h*0.2 
            t_center_x, t_center_y = room.a4.x +WALL_THICKNESS+(t_height+t_width)*0.5, room.a4.y + WALL_THICKNESS + t_height*0.5
            # Draw Table 
            ax.add_patch(Rectangle((t_center_x - t_width/2, t_center_y - t_height/2), t_width, t_height, color='#8d6e63', ec='#5d4037', lw=1.5, zorder=20))
            # Draw 4 Chairs 
            chair_spacing = t_width*0.2
            chair_dist = t_height/2 + t_height*0.25  
            # Chair offsets
            chair_positions = [
                (-t_width/4, chair_dist),  (t_width/4, chair_dist),  # Top side
                (-t_width/2 - t_height*0.25, 0), (t_width/2 + t_height*0.25, 0)  # Bottom side
            ]
            for cx_off, cy_off in chair_positions:
                ax.add_patch(Circle((t_center_x + cx_off, t_center_y + cy_off), t_height*0.25, color='#5d4037', zorder=20))


        elif room_name == "Normal1_Bedroom":
            b1_w, b1_h = min(nb_w*0.5, 11.0), min(nb_h*0.4, 7.0)
            bx = room.a4.x + 2.0
            by = room.a1.y - b1_h - WALL_THICKNESS 

            # Bed Base
            ax.add_patch(Rectangle((bx, by), b1_w, b1_h, color='white', ec=detail_color, lw=1, zorder=20))
            # Headboard
            ax.add_patch(Rectangle((bx, by), b1_w*0.09, b1_h, color='#475569', zorder=21))
            # Pillows
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8), b1_w*0.15, b1_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b1_h - 2.6), b1_w*0.15,b1_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            # Duvet
            ax.add_patch(Rectangle((bx + 3.0, by), b1_w - 3.0, b1_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            # Duvet fold line
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b1_h], color=detail_color, lw=1, ls='--', zorder=24)

        elif room_name == "Master_Bedroom":
            b2_w, b2_h = min(mb_w*0.4, 11.0), min(mb_h*0.4, 7.0)
            bx = room.a4.x + 2.0
            by = room.a4.y + 2.5

            # Bed Base
            ax.add_patch(Rectangle((bx, by), b2_w, b2_h, color='white', ec=detail_color, lw=1, zorder=20))
            # Headboard
            ax.add_patch(Rectangle((bx, by), b2_w*0.09, b2_h, color='#475569', zorder=21))
            # Pillows
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8), b2_w*0.15, b2_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b2_h - 2.6), b2_w*0.15, b2_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            # Duvet
            ax.add_patch(Rectangle((bx + 3.0, by), b2_w - 3.0, b2_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            # Duvet fold line
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b2_h], color=detail_color, lw=1, ls='--', zorder=24)

        elif room_name == "Normal2_Bedroom":
            b3_w, b3_h = min(guest_w*0.7, 10.0), min(guest_h*0.4, 6.0)
            bx = room.a4.x + guest_w*0.15
            by = room.a1.y - b3_h - WALL_THICKNESS

            # Bed Base
            ax.add_patch(Rectangle((bx, by), b3_w, b3_h, color='white', ec=detail_color, lw=1, zorder=20))
            # Headboard
            ax.add_patch(Rectangle((bx, by), b3_w*0.09, b3_h, color='#475569', zorder=21))
            # Pillows
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8), b3_w*0.15, b3_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b3_h - 2.6), b3_w*0.15, b3_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            # Duvet
            ax.add_patch(Rectangle((bx + 3.0, by), b3_w - 3.0, b3_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            # Duvet fold line
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b3_h], color=detail_color, lw=1, ls='--', zorder=24)

        elif room_name == "Bathroom" or room_name == "Common_Toilet":
            if "Bathroom" in room_name:
                rect_x, rect_y = room.a2.x * 0.1, room.a3.y * 1.1
                rect_w, rect_h = bath_w*0.4, bath_h*0.5
                ax.add_patch(Rectangle((rect_x, rect_y), rect_w, rect_h, color='#f1f5f9', ec='black', zorder=20))
                ax.add_patch(Ellipse((rect_x+rect_w*0.5, rect_y + rect_h*0.5), rect_w*0.8, rect_h*0.8, color='white', ec='#3b82f6', lw=0.8, zorder=21))
            elif "Common_Toilet" in room_name:
                rect_x, rect_y = room.a2.x - WALL_THICKNESS-toilet_w*0.3, room.a3.y+toilet_h*0.7- WALL_THICKNESS
                rect_w, rect_h = toilet_w*0.3,toilet_h*0.3
                ax.add_patch(Rectangle((rect_x, rect_y), rect_w, rect_h, color='#f1f5f9', ec='black', zorder=20))
                ax.add_patch(Ellipse((rect_x + rect_w*0.5, rect_y + rect_h*0.5), rect_w*0.8, rect_h*0.8, color='white', ec='#3b82f6', lw=0.8, zorder=21))

            if "Toilet" in room_name:
                tank_h = toilet_h*0.4
                tank_w = toilet_w*0.08
                ax.add_patch(Rectangle((room.a4.x + WALL_THICKNESS*2, room.a3.y + toilet_h* 0.3), tank_w, tank_h, color='white', ec='gray', zorder=21))
                ax.add_patch(Ellipse((room.a4.x + toilet_w*0.2, room.a3.y + toilet_h* 0.5), toilet_w*0.25,toilet_h*0.35, color='white', ec='gray', zorder=20))

        elif room_name == "Master_Toilet":
            rect_x, rect_y = room.a2.x - mt_w*0.3-WALL_THICKNESS, room.a3.y + mt_h*0.6 
            rect_w, rect_h = mt_w*0.3,mt_h*0.3
            ax.add_patch(Rectangle((rect_x, rect_y), rect_w, rect_h, color="#f1f5f9", ec='black', zorder=20))
            ax.add_patch(Ellipse((rect_x + rect_w*0.5, rect_y + rect_h*0.5),mt_w*0.22 ,mt_h*0.3, color='white', ec='#3b82f6', lw=0.8, zorder=21))

            if "Toilet" in room_name:
                tank_h = mt_h*0.15
                tank_w = mt_w*0.08
                ax.add_patch(Ellipse((room.a4.x + mt_w*0.2, room.a1.y - mt_h*0.5), mt_w*0.25, mt_h*0.35, color='white', ec='gray', zorder=20))
                ax.add_patch(Rectangle((room.a4.x + WALL_THICKNESS, room.a1.y - mt_h*0.8), tank_w, mt_h*0.6, color='white', ec='gray', zorder=21))
    #helper functions
    def draw_double_wall(ax, room):
        x, y = room.a4.x, room.a4.y
        w, h = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor="black", lw=1.5, zorder=5))
        ax.add_patch(Rectangle((x + WALL_THICKNESS, y + WALL_THICKNESS),
                            w - 2*WALL_THICKNESS, h - 2*WALL_THICKNESS,
                            fill=True, facecolor='white', edgecolor="black",
                            alpha=0.6, lw=0.8, zorder=4))

    def draw_door(ax, cx, cy, r, t1, t2):
        ax.add_patch(Arc((cx, cy), r*2, r*2, theta1=t1, theta2=t2, linewidth=1.5, color="black", zorder=12))
        ax.plot([cx, cx + r * math.cos(math.radians(t1))], [cy, cy + r * math.sin(math.radians(t1))], color="black", lw=1.5, zorder=13)
        ax.plot([cx, cx + r * math.cos(math.radians(t2))], [cy, cy + r * math.sin(math.radians(t2))], color="black", lw=1.0, ls="--", zorder=11)

    def draw_opening_v(ax, x, yc, w):
        ax.plot([x, x], [yc - w/2, yc + w/2], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_opening_h(ax, xc, y, w):
        ax.plot([xc - w/2, xc + w/2], [y, y], lw=4, color="white", zorder=11, solid_capstyle='butt')

    #drawing logic
    fig, ax = plt.subplots(figsize=(12, 9))
    wood_base = np.full((100, 100, 3), [0.8, 0.7, 0.5])
    noise = np.random.normal(0, 0.02, (100, 100, 3))
    wood_texture = np.clip(wood_base + noise, 0, 1)
    for i in range(0, 100, 5): wood_texture[:, i:i+2, :] -= 0.05
    ax.imshow(wood_texture, extent=[-5, PLOT_WIDTH + 5, -5, PLOT_HEIGHT + 5], aspect='auto', zorder=0)

    ax.add_patch(Rectangle((0, 0), PLOT_WIDTH, PLOT_HEIGHT, fill=False, lw=2, edgecolor="black", zorder=10))

    for name, room in layout.items():
        draw_double_wall(ax, room)
        draw_furniture(ax, name, room)
        x, y = room.a4.x, room.a4.y
        w, h_actual = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.text(x + w/2, y + h_actual/2, name.replace("_", " "), ha="center", va="center",
                fontsize=8, fontweight='bold', zorder=25,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    # Doors & Openings
    if PLOT_AREA>=3000:
        D_RAD = 2.0
    else:
        D_RAD = 1.7
    draw_opening_v(ax, PLOT_WIDTH - living_w, (kit_h+(living_h-guest_h)*0.5),(living_h-guest_h)*0.8) #living
    draw_opening_h(ax, (PLOT_WIDTH-living_w*1.2), kit_h, 4.3) #kitchen
    draw_door(ax, mb_w*0.8, mb_h, D_RAD, 270, 360) #master bed
    draw_door(ax, mt_w, mb_h - mt_h*0.5, D_RAD-1, 180, 270) #master bathroom
    draw_door(ax, toilet_w, PLOT_HEIGHT - nb_h - toilet_h*0.5, D_RAD-1, 180, 270) #toilet
    draw_door(ax, bath_w, mb_h + 0.5*bath_h, D_RAD-1, 180, 270)  #bathroom
    draw_door(ax, nb_w*0.95, PLOT_HEIGHT - nb_h, D_RAD, 90, 180)  #normal bed
    draw_door(ax, PLOT_WIDTH - living_w - guest_w/2, PLOT_HEIGHT - guest_h, D_RAD, 90, 180) #guest
    draw_door(ax, PLOT_WIDTH-living_w*0.2, PLOT_HEIGHT, D_RAD, 180, 270)   #entry door
    draw_door(ax, PLOT_WIDTH-bal_w , bal_h*0.08, D_RAD-1, 0, 90) #balcony

    #window placement
    draw_opening_v(ax, 0, PLOT_HEIGHT*0.9, 4) #normal
    draw_opening_h(ax, (PLOT_WIDTH*0.5), PLOT_HEIGHT, 4) #guest
    draw_opening_v(ax, 0, (mb_h+bath_h+mt_h*0.6), 1.8) #toilet
    draw_opening_v(ax, 0, (mb_h+bath_h*0.6), 1.8) #bathroom
    draw_opening_v(ax, 0, (mb_h-mt_h*0.6), 1.8) #master toilet
    draw_opening_h(ax, (mb_w*0.5), 0, 4) #master
    draw_opening_h(ax, (mb_w+ kit_w*0.5), 0, 4) #kitchen

    ax.set_aspect("equal")
    ax.set_xlim(-1, PLOT_WIDTH + 1)
    ax.set_ylim(-1, PLOT_HEIGHT + 1)
    plt.axis('off')

        #report and data preparation
    def dims(r): return round(r.a2.x-r.a1.x,2), round(r.a1.y-r.a4.y,2)

    def get_direction(r):
        cx=(r.a1.x+r.a2.x)/2; cy=(r.a1.y+r.a4.y)/2
        if cy > PLOT_HEIGHT*0.66: return "North"
        if cy < PLOT_HEIGHT*0.33: return "South"
        if cx > PLOT_WIDTH*0.66: return "East"
        if cx < PLOT_WIDTH*0.33: return "West"
        return "Central"

    # Compile Full Report Data
    full_report = {}
    for n, r in layout.items():
        w, h = dims(r)
        full_report[n] = {
            "area": float(r.area),
            "width": float(w),
            "height": float(h),
            "direction": get_direction(r)
        }

    # Save physical report
    report_path = f"layout_report_{layout_id}.txt"
    with open(report_path,"w") as f:
        f.write(f"ARCHITECTURAL REPORT | ID: {layout_id}\n")
        f.write(f"Generated: {timestamp} | Plot: {PLOT_AREA} sq.ft\n")
        f.write("-" * 55 + "\n")
        for name, data in full_report.items():
            f.write(f"{name:<12} {data['area']:<8} {data['width']}x{data['height']} {data['direction']}\n")

    # Save image
    img_path = f"layout_{layout_id}.png"
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    #final report
    return {
        "layout_id": layout_id,
        "image_path": img_path,
        "report_path": report_path,
        "timestamp": timestamp,
        "plot_metadata": {
            "total_area": float(PLOT_AREA),
            "width": float(round(PLOT_WIDTH, 2)),
            "height": float(round(PLOT_HEIGHT, 2))
        },
        "full_report": full_report  
    }