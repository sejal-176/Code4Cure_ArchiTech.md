def generate(plot_height: int, plot_width: int) -> dict:
    import uuid
    from datetime import datetime
    import matplotlib
    from ortools.sat.python import cp_model
    import math
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Arc, Circle, Ellipse
    from dataclasses import dataclass
    import numpy as np

    layout_id = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    PLOT_WIDTH = plot_width
    PLOT_HEIGHT = plot_height
    PLOT_AREA = PLOT_WIDTH * PLOT_HEIGHT

    rooms = {
        "Living": (14, 20),
        "Kitchen_Balcony": (2, 4),
        "Kitchen": (9, 12),
        "Normal_Bedroom": (8,12),
        "Guest_Bedroom": (8, 12),
        "Master_Bedroom": (9, 12),
        "Master_Toilet": (3, 5),
        "Common_Toilet": (2, 3),
        "Bathroom": (3, 5),
        "corridor": (12, 18)
    }


    model = cp_model.CpModel()
    area_vars = {}

    for room, (min_p, max_p) in rooms.items():
        min_area = int(PLOT_AREA * min_p / 100)
        max_area = int(PLOT_AREA * max_p / 100)
        area_vars[room] = model.NewIntVar(min_area, max_area, f"{room}_area")

    model.Add(sum(area_vars.values()) == PLOT_AREA)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No feasible solution found.")

    rooms = {room: solver.Value(var) for room, var in area_vars.items()}

    @dataclass
    class Point:
        x: float
        y: float

    @dataclass
    class Room:
        a1: Point  # top-left
        a2: Point  # top-right
        a3: Point  # bottom-right
        a4: Point  # bottom-left
        area: float


    PLOT_WIDTH = PLOT_AREA/40
    PLOT_HEIGHT = PLOT_AREA/PLOT_WIDTH
    WALL_THICKNESS = 0.6

    ratio = PLOT_HEIGHT/PLOT_WIDTH
    layout = {}

    def draw_door(ax, cx, cy, r, t1, t2):
        ax.add_patch(Arc((cx, cy), r*2, r*2, theta1=t1, theta2=t2, linewidth=1.5, color="black", zorder=12))
        ax.plot([cx, cx + r * math.cos(math.radians(t1))], [cy, cy + r * math.sin(math.radians(t1))], color="black", lw=1.5, zorder=13)
        ax.plot([cx, cx + r * math.cos(math.radians(t2))], [cy, cy + r * math.sin(math.radians(t2))], color="black", lw=1.0, ls="--", zorder=11)

    def draw_opening_v(ax, x, yc, w):
        ax.plot([x, x], [yc - w/2, yc + w/2], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_opening_h(ax, xc, y, w):
        ax.plot([xc - w/2, xc + w/2], [y, y], lw=4, color="white", zorder=11, solid_capstyle='butt')


    def draw_furniture(ax, room_name, room):
        fabric_color = '#94a3b8'
        detail_color = '#475569'
        wood_color = '#b5835a'

        rw, rh = (room.a2.x - room.a1.x), (room.a1.y - room.a4.y)


# FURNITURE LOGIC ---
        if room_name == "Living":
            v_h, v_w, h_l = 11.0, 2.5, 10.0
            sofa_x = room.a4.x + WALL_THICKNESS
            sofa_y_base = room.a1.y - WALL_THICKNESS - v_h
            ax.add_patch(Rectangle((sofa_x, sofa_y_base), v_w, v_h, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))
            ax.add_patch(Rectangle((sofa_x, sofa_y_base + v_h - v_w), h_l, v_w, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))
            for i in range(4):
                ax.add_patch(Rectangle((sofa_x + 0.2, sofa_y_base + (i * 2.2) + 0.2), v_w - 0.4, 1.8, fill=False, ec=detail_color, lw=0.6, zorder=21))
                ax.add_patch(Rectangle((sofa_x + 0.1, sofa_y_base + (i * 2.2) + 0.4), 0.6, 1.4, color=fabric_color, ec=detail_color, lw=0.5, zorder=22))
            for i in range(1, 4):
                ax.add_patch(Rectangle((sofa_x + (i * 2.5) + 0.2, sofa_y_base + v_h - v_w + 0.2), 2.1, v_w - 0.4, fill=False, ec=detail_color, lw=0.6, zorder=21))
                ax.add_patch(Rectangle((sofa_x + (i * 2.5) + 0.4, sofa_y_base + v_h - 0.7), 1.7, 0.5, color=fabric_color, ec=detail_color, lw=0.5, zorder=22))
            ax.add_patch(Rectangle((sofa_x + 4.5, sofa_y_base + 3), 5.5, 4.0, color=wood_color, ec=detail_color, alpha=0.9, zorder=22))
            ax.add_patch(Rectangle((room.a2.x - 2.2, sofa_y_base), 1.2, 7, color=wood_color, ec=detail_color, zorder=20))

        elif room_name == "Kitchen":
            counter_depth = 2.0
            ax.add_patch(Rectangle((room.a2.x - counter_depth - WALL_THICKNESS, room.a4.y + WALL_THICKNESS), counter_depth, (room.a2.y - room.a4.y - 2*WALL_THICKNESS), color='#e2e8f0', ec='#94a3b8', zorder=20))
            stove_w, stove_h = 1.6, 2.8
            stove_x = room.a2.x - counter_depth - WALL_THICKNESS + 0.2
            stove_y = room.a1.y - stove_h - WALL_THICKNESS - 2.0
            ax.add_patch(Rectangle((stove_x, stove_y), stove_w, stove_h, color='#334155', zorder=21))
            for dy in [0.6, 2.2]:
                ax.add_patch(Circle((stove_x + 0.8, stove_y + dy), 0.35, color='black', ec='white', lw=0.4, zorder=22))
            tw, th = 6.0, 3.5
            tx, ty = room.a4.x + WALL_THICKNESS + 2.0, room.a1.y - th - WALL_THICKNESS - 7.0
            ax.add_patch(Rectangle((tx, ty), tw, th, color='#8d6e63', ec='#5d4037', lw=1.5, zorder=20))
            cw, ch = 1.1, 1.1
            chair_color = '#a1887f'
            for offset_x in [1.0, 3.9]:
                ax.add_patch(Rectangle((tx + offset_x, ty + th - 0.2), cw, ch, color=chair_color, ec='#5d4037', zorder=19))
            for offset_y in [0.2, 1.2, 2.2]:
                ax.add_patch(Rectangle((tx - cw + 0.2, ty + offset_y), cw, ch, color=chair_color, ec='#5d4037', zorder=19))

        elif "Normal_Bedroom" in room_name:
            b1_w, b1_h = nb_w*0.5,nb_h*0.4
            bx, by = room.a4.x + WALL_THICKNESS, room.a1.y - b1_h - WALL_THICKNESS

        # bx, by = room.a4.x + 2.0, room.a4.y + 2.5
            ax.add_patch(Rectangle((bx, by), b1_w, b1_h, color='white', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), b1_w*0.09, b1_h, color='#475569', zorder=21))
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8), b1_w*0.2, b1_w*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b1_h - 2.6), b1_w*0.2, b1_w*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 3.0, by), b1_w - 3.0, b1_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b1_h], color=detail_color, lw=1, ls='--', zorder=24)
        elif "Master_Bedroom" in room_name:
            b2_w, b2_h = mb_w*0.5,mb_h*0.4
            bx, by = room.a4.x + WALL_THICKNESS, room.a4.y + WALL_THICKNESS

            ax.add_patch(Rectangle((bx, by), b2_w, b2_h, color='white', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), mb_w*0.09, b2_h, color='#475569', zorder=21))
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8),b2_w*0.2 , b2_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b2_h - 2.6), b2_w*0.2, b2_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 3.0, by), b2_w - 3.0, b2_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b2_h], color=detail_color, lw=1, ls='--', zorder=24)

        elif "Guest_Bedroom" in room_name:
            b3_w, b3_h = guest_w*0.4,guest_h*0.4
            bx, by = room.a4.x + WALL_THICKNESS, room.a1.y - b3_h - WALL_THICKNESS

            ax.add_patch(Rectangle((bx, by), b3_w, b3_h, color='white', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), b3_w*0.09, b3_h, color='#475569', zorder=21))
            ax.add_patch(Rectangle((bx + 1.0, by + 0.8), b3_w*0.2, b3_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 1.0, by + b3_h - 2.6), b3_w*0.2, b3_h*0.2, color='white', ec='gray', lw=0.5, zorder=22))
            ax.add_patch(Rectangle((bx + 3.0, by), b3_w - 3.0, b3_h, color=fabric_color, ec=detail_color, lw=1, zorder=23))
            ax.plot([bx + 3.0, bx + 3.0], [by, by + b3_h], color=detail_color, lw=1, ls='--', zorder=24)

        elif name == "Bathroom":
            sink_w, sink_h_val = bath_w*0.3, bath_h*0.15# Renamed sink_h to sink_h_val
            ax.add_patch(Rectangle((room.a4.x+bath_w*0.1, room.a4.y +(bath_h-sink_h_val)-WALL_THICKNESS), sink_w, sink_h_val, facecolor='white', edgecolor='gray', zorder=10))
            ax.add_patch(Ellipse((room.a4.x+bath_w*0.23, room.a4.y +(bath_h-sink_h_val)-WALL_THICKNESS+0.9), sink_w/2, sink_h_val/2, facecolor='white', edgecolor='#3b82f6', zorder=11))

        elif room_name in [ "Common_Toilet", "Master_Toilet"]:
            s_w, s_h = rw * 0.3, 1.5
            sx = room.a2.x - s_w - WALL_THICKNESS
            sy = room.a1.y - s_h - WALL_THICKNESS
            ax.add_patch(Rectangle((sx, sy), s_w, s_h, color='#f8fafc', ec='#94a3b8', zorder=20))
            ax.add_patch(Ellipse((sx + s_w/2, sy + s_h/2), s_w*0.8, s_h*0.7, color='white', ec='#3b82f6', lw=0.8, zorder=21))

            if "Toilet" in room_name:
                ax.add_patch(Rectangle((room.a4.x + WALL_THICKNESS + 0.5, room.a4.y + WALL_THICKNESS + 1.5), 1.5, 0.6, color='white', ec='gray', zorder=21))
                ax.add_patch(Ellipse((room.a4.x + WALL_THICKNESS + 1.25, room.a4.y + WALL_THICKNESS + 1.0), 1.2, 1.8, color='white', ec='gray', zorder=20))

    # layout logic
    mb_h = math.sqrt((rooms["Master_Bedroom"]+rooms["Master_Toilet"])*ratio)
    mb_w = (rooms["Master_Bedroom"]+rooms["Master_Toilet"])/ mb_h
    layout["Master_Bedroom"] = Room(Point(0, mb_h), Point(mb_w, mb_h), Point(mb_w, 0), Point(0, 0), rooms["Master_Bedroom"])
    mt_w = math.sqrt(rooms["Master_Toilet"]*1.2)
    mt_h = rooms["Master_Toilet"]/mb_w
    layout["Master_Toilet"] = Room(Point(0, mb_h), Point(mt_w, mb_h), Point(mt_w, mb_h - mt_h), Point(0, mb_h - mt_h), rooms["Master_Toilet"])
    kit_w = PLOT_WIDTH - mb_w
    kit_h = (rooms["Kitchen"]+rooms["Kitchen_Balcony"])/ kit_w
    layout["Kitchen"] = Room(Point(PLOT_WIDTH - kit_w, kit_h), Point(PLOT_WIDTH, kit_h), Point(PLOT_WIDTH, rooms["Kitchen_Balcony"]/kit_w), Point(PLOT_WIDTH - kit_w, rooms["Kitchen_Balcony"]/kit_w), rooms["Kitchen"])
    bal_w = kit_w
    bal_h = rooms["Kitchen_Balcony"] / kit_w
    layout["Kitchen_Balcony"] = Room(Point(PLOT_WIDTH - bal_w, bal_h), Point(PLOT_WIDTH, bal_h), Point(PLOT_WIDTH, 0), Point(PLOT_WIDTH - kit_w, 0), rooms["Kitchen_Balcony"])
    living_h = (PLOT_HEIGHT-kit_h)*0.68
    living_w = (rooms["Living"])/ living_h
    layout["Living"] = Room(Point(PLOT_WIDTH - living_w, kit_h+living_h), Point(PLOT_WIDTH, kit_h+living_h), Point(PLOT_WIDTH, kit_h), Point(PLOT_WIDTH - living_w, kit_h), rooms["Living"])
    guest_h = (PLOT_HEIGHT-kit_h-living_h)
    guest_w = rooms["Guest_Bedroom"] / guest_h
    layout["Guest_Bedroom"] = Room(Point(PLOT_WIDTH-guest_w, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT - guest_h), Point(PLOT_WIDTH-guest_w, PLOT_HEIGHT - guest_h), rooms["Guest_Bedroom"])
    nb_w = PLOT_WIDTH-guest_w
    nb_h = rooms["Normal_Bedroom"] / nb_w
    layout["Normal_Bedroom"] = Room(Point(0, PLOT_HEIGHT), Point(nb_w, PLOT_HEIGHT), Point(nb_w, PLOT_HEIGHT-nb_h), Point(0, PLOT_HEIGHT-nb_h), rooms["Normal_Bedroom"])
    up_remain_height = PLOT_HEIGHT-nb_h-mb_h
    bath_h = up_remain_height*0.6
    bath_w = rooms["Bathroom"] / bath_h
    layout["Bathroom"] = Room(Point(0, mb_h+bath_h), Point(bath_w, mb_h+bath_h), Point(bath_w, mb_h), Point(0, mb_h), rooms["Bathroom"])
    toilet_h = (up_remain_height - bath_h)
    toilet_w = rooms["Common_Toilet"] / toilet_h
    layout["Common_Toilet"] = Room(Point(0, PLOT_HEIGHT-nb_h), Point(toilet_w, PLOT_HEIGHT-nb_h), Point(toilet_w, PLOT_HEIGHT -nb_h- toilet_h), Point(0, PLOT_HEIGHT - nb_h- toilet_h), rooms["Common_Toilet"])

   #drawing 
    fig, ax = plt.subplots(figsize=(11, 14))
    res = 100
    wood_base = np.full((res, res, 3), [0.82, 0.71, 0.55])
    noise = np.random.normal(0, 0.02, (res, res, 3))
    wood_texture = np.clip(wood_base + noise, 0, 1)
    for i in range(0, res, 8): wood_texture[:, i:i+1, :] -= 0.05
    ax.imshow(wood_texture, extent=[-1, PLOT_WIDTH + 1, -1, PLOT_HEIGHT + 1], aspect='auto', zorder=0)

    for name, room in layout.items():
        x, y = room.a4.x, room.a4.y
        w, h = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, edgecolor='black', linewidth=2.5, zorder=10))
        ax.add_patch(plt.Rectangle((x + WALL_THICKNESS, y + WALL_THICKNESS), w - 2*WALL_THICKNESS, h - 2*WALL_THICKNESS, facecolor='white', alpha=0.4, edgecolor='black', linewidth=0.8, zorder=5))
        draw_furniture(ax, name, room)
        ax.text(x + w/2, y + h/2, name.replace("_", " "), ha="center", va="center", fontsize=9, fontweight='bold', zorder=25, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
    #openings
    draw_opening_v(ax, 0, PLOT_HEIGHT*0.9, 4) #normal
    draw_opening_h(ax, (PLOT_WIDTH*0.5), PLOT_HEIGHT, 4) #guest
    draw_opening_v(ax, 0, (mb_h+bath_h+mt_h*0.6), 1.8) #toilet
    draw_opening_v(ax, 0, (mb_h+bath_h*0.6), 1.8) #bathroom
    draw_opening_v(ax, 0, (mb_h-mt_h*0.6), 1.8) #master toilet
    draw_opening_h(ax, (mb_w*0.5), 0, 4) #master
    draw_opening_v(ax, PLOT_WIDTH, kit_h*0.8, 4) #kitchen
    draw_opening_v(ax,PLOT_WIDTH,PLOT_HEIGHT-guest_h-living_h*0.2,4)
    #doors
    # Doors & Openings
    D_RAD = 1.7
    draw_opening_v(ax, PLOT_WIDTH - living_w, (kit_h+(living_h-guest_h)*0.5),6) #livingD
    draw_opening_h(ax, (PLOT_WIDTH-living_w*1.13), kit_h, PLOT_WIDTH-mb_w-living_w-0.1) #kitchen
    draw_door(ax, mb_w*0.8, mb_h, D_RAD, 270, 360) #master bed
    draw_door(ax, mt_w, mb_h - mt_h*0.7, D_RAD-1, 180, 270) #master bathroom
    draw_door(ax, toilet_w, PLOT_HEIGHT - nb_h - toilet_h*0.7, D_RAD-1, 180, 270) #toilet
    draw_door(ax, bath_w, mb_h + 0.5*bath_h, D_RAD-1, 180, 270)  #bathroom
    draw_door(ax, nb_w*0.85, PLOT_HEIGHT - nb_h, D_RAD, 90, 180)  #normal bed
    draw_door(ax, PLOT_WIDTH - guest_w*0.8, PLOT_HEIGHT-guest_h, D_RAD, 90, 180) #guest
    #draw_door(ax, PLOT_WIDTH-living_w*0.4 , PLOT_HEIGHT, D_RAD, 0, 180)   #entry door
    draw_door(ax, PLOT_WIDTH-bal_w , bal_h*0.6, D_RAD-1, 0, 90) #balcony-master
    draw_door(ax,mb_w+bal_w*0.6,bal_h,D_RAD-1,90,180)#balcony_kitchen
    draw_door(ax,PLOT_WIDTH,PLOT_HEIGHT-guest_h-living_h*0.8,D_RAD,90,180)#living entry

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
    