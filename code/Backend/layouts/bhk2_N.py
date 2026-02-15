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
    matplotlib.use('Agg')  
    
    layout_id = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    PLOT_WIDTH = plot_width
    PLOT_HEIGHT = plot_height
    PLOT_AREA = PLOT_WIDTH * PLOT_HEIGHT

    rooms_to_optimize = {
        "Living": (20, 25),             
        "Kitchen": (12, 14),            
        "Balcony_K": (5, 6),            
        "Balcony_B": (4, 5),            
        "Bedroom1": (18, 20),           
        "Bedroom2": (17, 19),           
        "Toilet": (2, 3),               
        "Bathroom": (2, 3),             
        "Pooja": (2, 3),                 
        "Corridor": (6, 10)  
    }

    model = cp_model.CpModel()
    area_vars = {}

    for room, (min_p, max_p) in rooms_to_optimize.items():
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

    #data structure
    @dataclass
    class Point:
        x: float
        y: float

    @dataclass
    class Room:
        a1: Point; a2: Point; a3: Point; a4: Point; area: float

    #layout generation
    WALL_THICKNESS = 0.5
    layout = {}

    #living+pooja
    lp_area = rooms["Living"] + rooms["Pooja"]

    if PLOT_WIDTH > PLOT_HEIGHT:
        living_h_ratio = 0.5
    else:
        living_h_ratio = 0.65

    living_h = PLOT_HEIGHT * living_h_ratio
    living_w = lp_area / living_h
    layout["Living"] = Room(Point(PLOT_WIDTH - living_w, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT - living_h), Point(PLOT_WIDTH - living_w, PLOT_HEIGHT - living_h), rooms["Living"])

    pooja_w = math.sqrt(rooms["Pooja"])
    layout["Pooja"] = Room(Point(PLOT_WIDTH - pooja_w, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT), Point(PLOT_WIDTH, PLOT_HEIGHT - pooja_w), Point(PLOT_WIDTH - pooja_w, PLOT_HEIGHT - pooja_w), rooms["Pooja"])


    #kitchen-balcony_k
    kb_area = rooms["Balcony_K"] + rooms["Kitchen"]
    kb_height = PLOT_HEIGHT-living_h
    kb_width = kb_area / kb_height

    kitchen_h = rooms["Kitchen"] / kb_width
    layout["Kitchen"] = Room(Point(PLOT_WIDTH - kb_width, PLOT_HEIGHT - living_h), Point(PLOT_WIDTH, PLOT_HEIGHT - living_h), Point(PLOT_WIDTH, PLOT_HEIGHT - living_h - kitchen_h), Point(PLOT_WIDTH - kb_width, PLOT_HEIGHT - living_h - kitchen_h), rooms["Kitchen"])

    bal_k_h = rooms["Balcony_K"] / kb_width
    layout["Balcony_K"] = Room(Point(PLOT_WIDTH - kb_width, bal_k_h), Point(PLOT_WIDTH, bal_k_h), Point(PLOT_WIDTH, 0), Point(PLOT_WIDTH - kb_width, 0), rooms["Balcony_K"])

    #bedroom1+balcony_b
    bb_width = PLOT_WIDTH - kb_width
    bb_height = (rooms["Bedroom1"] + rooms["Balcony_B"]) / bb_width
    bed1_w = rooms["Bedroom1"] / bb_height
    layout["Bedroom1"] = Room(Point(bb_width - bed1_w, bb_height), Point(bb_width, bb_height), Point(bb_width, 0), Point(bb_width - bed1_w, 0), rooms["Bedroom1"])
    layout["Balcony_B"] = Room(Point(0, bb_height), Point(rooms["Balcony_B"] / bb_height, bb_height), Point(rooms["Balcony_B"] / bb_height, 0), Point(0, 0), rooms["Balcony_B"])

    #bed
    bed2_w = PLOT_WIDTH - living_w
    bed2_h = rooms["Bedroom2"] / bed2_w
    layout["Bedroom2"] = Room(Point(0, PLOT_HEIGHT), Point(bed2_w, PLOT_HEIGHT), Point(bed2_w, PLOT_HEIGHT - bed2_h), Point(0, PLOT_HEIGHT - bed2_h), rooms["Bedroom2"])

    #toilet+bathroom
    free_h = PLOT_HEIGHT - bed2_h - bb_height
    bath_h =free_h/2
    bath_w = rooms["Bathroom"] / bath_h
    toilet_h = free_h/2
    toilet_w = rooms["Toilet"] / toilet_h
    layout["Toilet"] = Room(Point(0, PLOT_HEIGHT - bed2_h), Point(rooms["Toilet"] / (free_h/2), PLOT_HEIGHT - bed2_h), Point(rooms["Toilet"] / (free_h/2), bb_height + free_h/2), Point(0, bb_height + free_h/2), rooms["Toilet"])
    layout["Bathroom"] = Room(Point(0, bb_height + free_h/2), Point(rooms["Bathroom"] / (free_h/2), bb_height + free_h/2), Point(rooms["Bathroom"] / (free_h/2), bb_height), Point(0, bb_height), rooms["Bathroom"])
    
    

    # Furniture logic
    def draw_furniture(ax, room_name, room):
        fabric_color = '#94a3b8'
        detail_color = '#475569'
        wood_color = '#b5835a'
        if room_name == "Living":
            # --- ENHANCED L-SHAPED SOFA (Bottom-Right) ---
            sofa_x_base = room.a2.x - 11.5 - WALL_THICKNESS
            sofa_y_base = room.a3.y + WALL_THICKNESS

            # 1. Drop Shadow (Subtle depth)
            ax.add_patch(Rectangle((sofa_x_base + 0.2, sofa_y_base - 0.2), 11.5, 3.2, color='black', alpha=0.1, zorder=19))
            ax.add_patch(Rectangle((room.a2.x - 3.2 - WALL_THICKNESS, sofa_y_base), 3.2, 8.2, color='black', alpha=0.1, zorder=19))

            # 2. Main Sofa Body
            # Horizontal base
            ax.add_patch(Rectangle((sofa_x_base, sofa_y_base), 11.5, 3.0, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))
            # Vertical base (the L-extension)
            ax.add_patch(Rectangle((room.a2.x - 3.0 - WALL_THICKNESS, sofa_y_base), 3.0, 8.0, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))

            # 3. Armrests (Rounded look)
            ax.add_patch(Rectangle((sofa_x_base, sofa_y_base), 0.8, 3.0, color=detail_color, alpha=0.3, zorder=21))
            ax.add_patch(Rectangle((room.a2.x - 3.0 - WALL_THICKNESS, sofa_y_base + 7.2), 3.0, 0.8, color=detail_color, alpha=0.3, zorder=21))

            # 4. Cushions and Pillows
            # Horizontal cushions
            for i in range(3):
                cx = sofa_x_base + 1.0 + (i * 2.6)
                # Seat cushion
                ax.add_patch(Rectangle((cx, sofa_y_base + 0.2), 2.4, 2.6, fill=False, ec=detail_color, lw=0.7, zorder=22))
                # Decorative Pillow
                ax.add_patch(Rectangle((cx + 0.4, sofa_y_base + 2.2), 1.6, 0.6, color='white', ec=detail_color, lw=0.5, alpha=0.6, zorder=23))

            # 5. Living Room Center Coffee Table
            # Placed relative to the sofa's inner corner
            ax.add_patch(Rectangle((sofa_x_base + 2.0, sofa_y_base + 4.5), 4.5, 2.5, facecolor=wood_color, edgecolor='#5c4033', lw=1.2, zorder=22))
            # Glass top effect
            ax.add_patch(Rectangle((sofa_x_base + 2.3, sofa_y_base + 4.8), 3.9, 1.9, facecolor='#f1f5f9', alpha=0.5, edgecolor=None, zorder=23))

            # 6. Center Dining Table (Existing)
            room_w, room_h = room.a2.x - room.a1.x, room.a1.y - room.a4.y
            table_w, table_h = 6.0, 4.0
            tx, ty = room.a4.x + (room_w / 2) - (table_w / 2), room.a4.y + (room_h / 2) - (table_h / 2)
            ax.add_patch(Rectangle((tx, ty), table_w, table_h, facecolor=wood_color, edgecolor='#5c4033', lw=1.5, zorder=22))
        
        elif room_name == "Kitchen":
            ax.add_patch(Rectangle((room.a2.x - kb_width*0.15- WALL_THICKNESS, room.a3.y + WALL_THICKNESS), (kb_width*0.15), (kitchen_h-2*WALL_THICKNESS), color='#e2e8f0', ec='#94a3b8', zorder=20))
            stove_x, stove_y = room.a2.x - kb_width*0.15, room.a4.y + (room.a1.y - room.a4.y) / 2 - 1.5
            ax.add_patch(Rectangle((stove_x, stove_y), kb_width*0.1, kitchen_h*0.3, color='#334155', zorder=21))
            for i in range(3):
                ax.add_patch(Circle((stove_x + kb_width*0.05, stove_y + kitchen_h*0.04 + i*(kitchen_h*0.25/3)), kitchen_h*0.025, color='black', ec='white', lw=0.3, zorder=22))
            
            t_width, t_height = kb_width*0.3, kitchen_h*0.2 
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
        
        elif "Bedroom" in room_name:
            bed_w, bed_h = min(bed2_w*0.6,12), min(bed2_h*0.4,10)
            bx, by = room.a4.x + WALL_THICKNESS, room.a1.y - bed_h - 2*WALL_THICKNESS
            ax.add_patch(Rectangle((bx, by), bed_w, bed_h, color='#cbd5e1', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), 0.5, bed_h, color=detail_color, zorder=21))
            for py in [by + bed_h*0.1, by + bed_h*0.6]:
                ax.add_patch(Rectangle((bx + 0.8, py), bed_w*0.15, bed_h*0.3, color='white', ec='gray', lw=0.5, zorder=22))
            ax.plot([bx + 3, bx + 3], [by, by + bed_h], color=detail_color, lw=0.8, ls='--', zorder=21)
            if room_name == "Bedroom1":
                tx, ty = room.a2.x - 6 - WALL_THICKNESS, room.a3.y + WALL_THICKNESS
                ax.add_patch(Rectangle((tx, ty), 6, 2.5, color=wood_color, ec='#5c4033', lw=1, zorder=20))
                ax.add_patch(Rectangle((tx + 2, ty + 0.5), 2, 1.5, color='#334155', zorder=21))
                ax.add_patch(Circle((tx + 3, ty + 3.5), 0.8, color='#475569', zorder=20))
            elif room_name == "Bedroom2":
                tx, ty = room.a2.x - 2.5 - WALL_THICKNESS, room.a3.y + 2
                ax.add_patch(Rectangle((tx, ty), 2.5, 6, color=wood_color, ec='#5c4033', lw=1, zorder=20))
                ax.add_patch(Rectangle((tx + 0.5, ty + 2), 1.5, 2, color='#334155', zorder=21))
                ax.add_patch(Circle((tx - 1.2, ty + 3), 0.8, color='#475569', zorder=20))
        elif room_name == "Bathroom":
            ax.add_patch(Rectangle((room.a2.x-bath_w*0.9 , room.a4.y + bath_h*0.2), bath_w*0.5, bath_h*0.5, color='#f1f5f9', ec='black', zorder=20))
            ax.add_patch(Ellipse((room.a2.x - bath_w*0.65, room.a4.y + bath_h*0.45), bath_w*0.4, bath_h*0.4, color='white', ec='#3b82f6', lw=0.8, zorder=21))
        elif room_name == "Toilet":
            tank_height = 0.8
            bowl_y_center = room.a1.y - WALL_THICKNESS - tank_height
            ax.add_patch(Rectangle((room.a4.x +WALL_THICKNESS, room.a1.y - WALL_THICKNESS - tank_height), toilet_w*0.2, tank_height, color='white', ec='gray', zorder=21))
            ax.add_patch(Ellipse((room.a4.x + WALL_THICKNESS + toilet_w*0.1, room.a1.y - WALL_THICKNESS - tank_height-toilet_h*0.2), toilet_w*0.15, toilet_h*0.5, color='white', ec='gray', zorder=20))

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
        x_open = cx + r * math.cos(math.radians(t1))
        y_open = cy + r * math.sin(math.radians(t1))
        ax.plot([cx, x_open], [cy, y_open], color="black", lw=1.5, zorder=13)
        x_closed = cx + r * math.cos(math.radians(t2))
        y_closed = cy + r * math.sin(math.radians(t2))
        ax.plot([cx, x_closed], [cy, y_closed], color="black", lw=1.0, ls="--", zorder=11)
    # GLOBAL OPENING FUNCTIONS
    def draw_opening_v(ax, x, yc, w):
        ax.plot([x, x], [yc - w/2, yc + w/2], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_opening_h(ax, xc, y, w):
        ax.plot([xc - w/2, xc + w/2], [y, y], lw=4, color="white", zorder=11, solid_capstyle='butt')

    
    #plottting
    fig, ax = plt.subplots(figsize=(14, 10))

    # Wood Background
    wood_base = np.full((100, 100, 3), [0.8, 0.7, 0.5])
    noise = np.random.normal(0, 0.02, (100, 100, 3))
    wood_texture = np.clip(wood_base + noise, 0, 1)
    for i in range(0, 100, 5): wood_texture[:, i:i+2, :] -= 0.05
    ax.imshow(wood_texture, extent=[-5, PLOT_WIDTH + 5, -5, PLOT_HEIGHT + 5], aspect='auto', zorder=0)

    ax.add_patch(Rectangle((0, 0), PLOT_WIDTH, PLOT_HEIGHT, fill=False, lw=2, edgecolor="black", zorder=10))

    for name, room in layout.items():
        draw_double_wall(ax, room)
        draw_furniture(ax, name, room)
        w_curr, h_curr = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.text(room.a4.x + w_curr / 2, room.a4.y + h_curr / 2, name, ha="center", va="center",
                fontsize=9, fontweight='bold', zorder=25, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        # Doors
        if name == "Balcony_K": draw_door(ax, room.a1.x + w_curr * 0.5, room.a1.y, 1.2, 270, 360)
        elif name == "Bedroom1":
            draw_door(ax, room.a4.x, room.a4.y + h_curr * 0.1, 1.5, 0, 90)
            draw_door(ax, room.a1.x + w_curr * 0.8, room.a1.y, 1.5, 270, 360)
        elif name == "Bedroom2": draw_door(ax, room.a4.x + w_curr * 0.6, room.a4.y, 1.5, 0, 90)
        elif name == "Toilet" or name == "Bathroom": draw_door(ax, room.a3.x, room.a4.y + h_curr * 0.4, 1.0, 90, 180)
        elif name == "Pooja": draw_door(ax, room.a4.x + w_curr * 0.8, room.a4.y, 1.2, 90, 180)
        elif name == "Living":draw_door(ax,PLOT_WIDTH-pooja_w-(living_w-pooja_w)*0.3,PLOT_HEIGHT,1.5,180,270)

    # Window Openings
    draw_opening_h(ax,bb_width*0.6, 0, 4) #bed1
    draw_opening_v(ax, 0, bb_height+free_h*0.3, 1.5) #bathroom
    draw_opening_v(ax,0 , bb_height+free_h*0.8 , 1.5) #toilet
    draw_opening_h(ax, bed2_w*0.6, PLOT_HEIGHT, 4)#bed2
    draw_opening_v(ax, PLOT_WIDTH, kitchen_h*0.9, 5) #Kitchen
    draw_opening_v(ax, PLOT_WIDTH, PLOT_HEIGHT-living_h*0.6, 4)#living
    if PLOT_WIDTH > PLOT_HEIGHT:
        draw_opening_v(ax, (PLOT_WIDTH-kb_width), (PLOT_HEIGHT-living_h-(kb_height-bb_height)*0.5), min(kb_height-bb_height, 4)) #kitchen-opening
        draw_opening_v(ax, (PLOT_WIDTH-living_w), (PLOT_HEIGHT-bed2_h-(living_h-bed2_h)*0.5), min(living_h-bed2_h, 4)) #Living-opening
    else:
        draw_opening_h(ax, (PLOT_WIDTH-living_w)-(kb_width-living_w)*0.5, kb_height, min(kb_width-living_w, 4)) #kitchen-opening
        draw_opening_v(ax, (PLOT_WIDTH-living_w), (PLOT_HEIGHT-bed2_h-(living_h-bed2_h)*0.5), min(living_h-bed2_h, 4)) #Living-opening

    ax.set_aspect("equal")
    ax.set_xlim(-1, PLOT_WIDTH + 1); ax.set_ylim(-1, PLOT_HEIGHT + 1)
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
    