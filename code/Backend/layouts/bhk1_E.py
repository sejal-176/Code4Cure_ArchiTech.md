def generate(plot_height: int, plot_width: int) -> dict:
    import uuid
    from datetime import datetime
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    from dataclasses import dataclass
    from matplotlib.patches import Arc, Rectangle, Circle, Ellipse
    from ortools.sat.python import cp_model
    import matplotlib
    matplotlib.use("Agg")

    #global metadata
    layout_id = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #area optimization
    PLOT_WIDTH = plot_width
    PLOT_HEIGHT = plot_height
    PLOT_AREA = PLOT_HEIGHT*PLOT_WIDTH
    model = cp_model.CpModel()

    living   = model.NewIntVar(0, PLOT_AREA, "Living")
    bedroom  = model.NewIntVar(0, PLOT_AREA, "Bedroom")
    kitchen  = model.NewIntVar(0, PLOT_AREA, "Kitchen")
    bathroom = model.NewIntVar(0, PLOT_AREA, "Bathroom")
    toilet   = model.NewIntVar(0, PLOT_AREA, "Toilet")
    gallery  = model.NewIntVar(0, PLOT_AREA, "Gallery")
    corridor = model.NewIntVar(0, PLOT_AREA, "Corridor")

    def percent(v, l, h):
        model.Add(v * 100 >= l * PLOT_AREA)
        model.Add(v * 100 <= h * PLOT_AREA)

    percent(living,36,40); percent(bedroom,25,32)
    percent(kitchen,18,20); percent(bathroom,8,10)
    percent(toilet,4,6); percent(gallery,4,6)
    percent(corridor,4,6)

    model.Maximize(living + bedroom + kitchen + bathroom + toilet + gallery+ corridor)
    model.Add(living + bedroom + kitchen + bathroom + toilet + gallery + corridor <= PLOT_AREA)

    solver = cp_model.CpSolver()
    if solver.Solve(model) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise Exception("No feasible layout")

    rooms = {
        "Living": solver.Value(living),
        "Bedroom": solver.Value(bedroom),
        "Kitchen": solver.Value(kitchen),
        "Bathroom": solver.Value(bathroom),
        "Toilet": solver.Value(toilet),
        "Gallery": solver.Value(gallery),
        "corridor": solver.Value(corridor),
    }

    #data structures
    @dataclass
    class Point: x: float; y: float
    @dataclass
    class Room: a1: Point; a2: Point; a3: Point; a4: Point; area: float

    #layout generation
    layout = {}

    if PLOT_WIDTH > PLOT_HEIGHT:
        living_h_ratio = 0.55
    else:
        living_h_ratio = 0.65

    living_h = PLOT_HEIGHT * living_h_ratio
    living_w = rooms["Living"] / living_h
    layout["Living"] = Room(
        Point(PLOT_WIDTH-living_w,PLOT_HEIGHT),
        Point(PLOT_WIDTH,PLOT_HEIGHT),
        Point(PLOT_WIDTH,PLOT_HEIGHT-living_h),
        Point(PLOT_WIDTH-living_w,PLOT_HEIGHT-living_h),
        rooms["Living"]
    )

    bed_w = PLOT_WIDTH-living_w
    bed_h = rooms["Bedroom"] / bed_w
    layout["Bedroom"] = Room(
        Point(0,PLOT_HEIGHT),Point(bed_w,PLOT_HEIGHT),
        Point(bed_w,PLOT_HEIGHT-bed_h),Point(0,PLOT_HEIGHT-bed_h),
        rooms["Bedroom"]
    )

    bath_h = PLOT_HEIGHT - bed_h
    bath_w = rooms["Bathroom"] / bath_h
    layout["Bathroom"] = Room(
        Point(0,bath_h),Point(bath_w,bath_h),Point(bath_w,0),Point(0,0),
        rooms["Bathroom"]
    )

    KG_h = PLOT_HEIGHT - living_h
    KG_w = (rooms["Kitchen"]+rooms["Gallery"]) / KG_h
    k_h = rooms["Kitchen"] / KG_w

    layout["Kitchen"] = Room(
        Point(PLOT_WIDTH-KG_w,PLOT_HEIGHT-living_h),
        Point(PLOT_WIDTH,PLOT_HEIGHT-living_h),
        Point(PLOT_WIDTH,layout["Living"].a3.y-k_h),
        Point(PLOT_WIDTH-KG_w,layout["Living"].a3.y-k_h),
        rooms["Kitchen"]
    )

    layout["Gallery"] = Room(
        Point(PLOT_WIDTH-KG_w,layout["Kitchen"].a3.y),
        Point(PLOT_WIDTH,layout["Kitchen"].a3.y),
        Point(PLOT_WIDTH,0),Point(PLOT_WIDTH-KG_w,0),
        rooms["Gallery"]
    )

    toilet_w = PLOT_WIDTH - bath_w - KG_w
    toilet_h = rooms["Toilet"] / toilet_w
    layout["Toilet"] = Room(
        Point(bath_w,toilet_h),
        Point(PLOT_WIDTH-KG_w,toilet_h),
        Point(PLOT_WIDTH-KG_w,0),Point(bath_w,0),
        rooms["Toilet"]
    )

    #drawing utilities
    WALL_THICKNESS = 0.8
    def draw_double_wall(ax, room):
        x, y = room.a4.x, room.a4.y
        w, h = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor="black", lw=2.5))
        ax.add_patch(Rectangle(
            (x + WALL_THICKNESS, y + WALL_THICKNESS),
            w - 2*WALL_THICKNESS, h - 2*WALL_THICKNESS,
            fill=True, facecolor='white', alpha=0.6
        ))

    def draw_door(ax, cx, cy, r, t1, t2):
        ax.add_patch(Arc((cx, cy), r*2, r*2, theta1=t1, theta2=t2, linewidth=1.5, color="black", zorder=12))
        ax.plot([cx, cx + r * math.cos(math.radians(t1))], [cy, cy + r * math.sin(math.radians(t1))], color="black", lw=1.5, zorder=13)
        ax.plot([cx, cx + r * math.cos(math.radians(t2))], [cy, cy + r * math.sin(math.radians(t2))], color="black", lw=1.0, ls="--", zorder=11)

    def draw_opening_v(ax, x, yc, w):
        ax.plot([x, x], [yc - w/2, yc + w/2], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_opening_h(ax, xc, y, w):
        ax.plot([xc - w/2, xc + w/2], [y, y], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_furniture(ax, name, room):
        x, y = room.a4.x + WALL_THICKNESS, room.a4.y + WALL_THICKNESS
        w, h = (room.a2.x - room.a1.x) - 2*WALL_THICKNESS, (room.a1.y - room.a4.y) - 2*WALL_THICKNESS
        fabric_color, detail_color, wood_color = '#94a3b8', '#475569', '#b5835a'

        if name == "Bedroom":
            
            bed1_w, bed1_h_val = bed_w*0.65, bed_h*0.3 
            bx, by = room.a4.x + WALL_THICKNESS, room.a1.y - bed1_h_val - WALL_THICKNESS
            ax.add_patch(Rectangle((bx, by), bed1_w, bed1_h_val, color='#cbd5e1', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), 0.5, bed1_h_val, color=detail_color, zorder=21))
            for py in [by +bed1_h_val*0.05, by + bed1_h_val*0.55]:
                ax.add_patch(Rectangle((bx + 0.8, py), 1.5, bed1_h_val*0.4, color='white', ec='gray', lw=0.5, zorder=22))
            ax.plot([bx + 3, bx + 3], [by, by + bed1_h_val], color=detail_color, lw=0.8, ls='--', zorder=21)
            tx, ty = room.a2.x - bed_w*0.15 - WALL_THICKNESS, room.a3.y + bed_h*0.2
            table_w, table_h = bed_w*0.15, bed_h*0.3
            ax.add_patch(Rectangle((tx, ty+1), bed_w*0.15, bed_h*0.3, color=wood_color, ec='#5c4033', lw=1, zorder=20))
            ax.add_patch(Rectangle((tx + 0.5, ty + 3), table_w*0.5, table_h*0.4, color='#334155', zorder=21))
            ax.add_patch(Circle((tx - 1.2, ty + 4), bed_w*0.05, color='#475569', zorder=20))

        elif name == "Kitchen":
            ax.add_patch(Rectangle((room.a2.x - KG_w*0.15- WALL_THICKNESS, room.a3.y + WALL_THICKNESS), (KG_w*0.15), (k_h-2*WALL_THICKNESS), color='#e2e8f0', ec='#94a3b8', zorder=20))
            stove_x, stove_y = room.a2.x - KG_w*0.15, room.a4.y + (room.a1.y - room.a4.y) / 2 - 1.5
            ax.add_patch(Rectangle((stove_x, stove_y), KG_w*0.1, k_h*0.3, color='#334155', zorder=21))
            for i in range(3):
                ax.add_patch(Circle((stove_x + KG_w*0.05, stove_y + k_h*0.04 + i*(k_h*0.25/3)), k_h*0.025, color='black', ec='white', lw=0.3, zorder=22))
           
            t_width, t_height = KG_w*0.3, k_h*0.2 
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

        elif name == "Living":
            
            sofa_x = room.a4.x + WALL_THICKNESS
            sofa_y_base = room.a4.y + (living_h)*0.4
            v_h, v_w, h_l = (living_h)*0.6-living_w*0.18, living_w*0.15, living_w*0.45

            # Sofa
            ax.add_patch(Rectangle((sofa_x, sofa_y_base), v_w, v_h, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))
            ax.add_patch(Rectangle((sofa_x, sofa_y_base + v_h), h_l, v_w, color=fabric_color, ec=detail_color, lw=1.2, zorder=20))

            # Cushions
            for i in range(int(min(4, v_h/2.2))):
                ax.add_patch(Rectangle((sofa_x + 0.2, sofa_y_base + (i * 2.2) + 0.2), v_w - 0.4, 1.8, fill=False, ec=detail_color, lw=0.6, zorder=21))
                ax.add_patch(Rectangle((sofa_x + 0.1, sofa_y_base + (i * 2.2) + 0.4), 0.6, 1.4, color=fabric_color, ec=detail_color, lw=0.5, zorder=22))

            for i in range(1, int(min(4, h_l/2.5+1))):
                ax.add_patch(Rectangle((sofa_x + (i * 2.5) + 0.2, sofa_y_base + v_h + 0.2), 2.1, v_w - 0.4, fill=False, ec=detail_color, lw=0.6, zorder=21))
                ax.add_patch(Rectangle((sofa_x + (i * 2.5) + 0.4, sofa_y_base + v_h + v_w*0.8), 1.7, 0.5, color=fabric_color, ec=detail_color, lw=0.5, zorder=22))

            # Coffee Table
            ax.add_patch(Rectangle((sofa_x + v_w*1.2, sofa_y_base+v_h*0.5), h_l*0.3, v_h*0.4, color=wood_color, ec=detail_color, alpha=0.9, zorder=22))

            # TV Unit
            ax.add_patch(Rectangle((room.a2.x - 2.2-WALL_THICKNESS, sofa_y_base), living_w*0.08-WALL_THICKNESS, living_h*0.3, color=wood_color, ec=detail_color, zorder=20))
        
        elif name == "Bathroom":
            sink_w, sink_h_val = bath_w*0.3, bath_h*0.2
            ax.add_patch(Rectangle((room.a4.x+bath_w*0.1, room.a4.y +(bath_h-sink_h_val)-WALL_THICKNESS), sink_w, sink_h_val, facecolor='white', edgecolor='gray', zorder=10))
            ax.add_patch(Ellipse((room.a4.x+bath_w*0.23, room.a4.y +(bath_h-sink_h_val)-WALL_THICKNESS+sink_h_val*0.5), sink_w/2, sink_h_val/2, facecolor='white', edgecolor='#3b82f6', zorder=11))
        elif name == "Toilet":
            tank_w, tank_h_val = toilet_w*0.3, toilet_h*0.1
            ax.add_patch(Ellipse((room.a4.x + toilet_w*0.5, room.a4.y + tank_h_val + 2*WALL_THICKNESS), toilet_w*0.18, toilet_h*0.4, facecolor='white', edgecolor='gray', zorder=10))
            ax.add_patch(Rectangle((room.a4.x + toilet_w*0.5 - tank_w/2, room.a4.y+WALL_THICKNESS), tank_w, tank_h_val, facecolor='white', edgecolor='gray', zorder=10))
            

    # matplotlib figure setup
    fig, ax = plt.subplots(figsize=(14, 10))

    # Background Texture
    wood_base = np.full((100, 100, 3), [0.82, 0.71, 0.55])
    noise = np.random.normal(0, 0.02, (100, 100, 3))
    wood_texture = np.clip(wood_base + noise, 0, 1)
    for i in range(0, 100, 6): wood_texture[:, i:i+1, :] -= 0.06
    ax.imshow(wood_texture, extent=[-2, PLOT_WIDTH+2, -2, PLOT_HEIGHT+2], aspect='auto', zorder=0)

    for name, room in layout.items():
        draw_double_wall(ax, room)
        draw_furniture(ax, name, room)

        # Labels
        tx_offset, ty_offset = 0, 0

        ax.text(room.a4.x + (room.a2.x-room.a1.x)/2 + tx_offset,
                (room.a4.y + (room.a1.y-room.a4.y)/2) + ty_offset,
                f"{name}", ha="center", va="center", fontsize=10, weight='bold', zorder=30,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.3'))
    
    # Openings & Doors
    draw_opening_h(ax,(bath_w+toilet_w*0.5), 0 , toilet_w*0.3) #Toilet
    draw_opening_h(ax, (bed_w*0.5), PLOT_HEIGHT, bed_w*0.4) #bed
    draw_opening_h(ax,(bath_w*0.5) , 0, bath_w*0.4) #bathroom
    draw_opening_v(ax, PLOT_WIDTH, (KG_h-k_h*0.5), min(k_h*0.5,4))#kitchen
    draw_opening_v(ax, PLOT_WIDTH, PLOT_HEIGHT-living_h*0.2, min(living_h*0.4,5)) #living
    draw_opening_v(ax, PLOT_WIDTH-KG_w, toilet_h+(KG_h-toilet_h)*0.5,min(KG_h-toilet_h, 3))#kitchen-door
    if PLOT_WIDTH > PLOT_HEIGHT:
        draw_opening_h(ax, (PLOT_WIDTH-living_w*0.9), PLOT_HEIGHT-living_h,min(living_w-KG_w,3))
    else:
        draw_opening_v(ax, (PLOT_WIDTH-living_w), KG_h+(living_h-bed_h)*0.5,min(living_h-bed_h,3))
    
    
    D_RAD=1.7
    if PLOT_WIDTH > PLOT_HEIGHT:
        draw_door(ax, bed_w, bath_h+(bed_h-living_h)*0.6, D_RAD, 180,270)
    else:
        draw_door(ax, bath_w+(bed_w-bath_w)*0.5, layout["Bedroom"].a3.y, D_RAD, 0,90)

    draw_door(ax, layout["Kitchen"].a4.x +KG_w*0.3+k_h*0.5+WALL_THICKNESS , layout["Kitchen"].a4.y, D_RAD, 90, 180)
    draw_door(ax, layout["Bathroom"].a2.x, toilet_h+(bath_h-toilet_h)*0.5, D_RAD-0.5, 180, 270)
    draw_door(ax, layout["Toilet"].a1.x + 2, layout["Toilet"].a1.y, D_RAD-0.5, 270, 360)
    draw_door(ax, PLOT_WIDTH, PLOT_HEIGHT-living_h*0.7, D_RAD, 180, 270)

    ax.set_aspect("equal")
    ax.set_xlim(-1, PLOT_WIDTH + 1)
    ax.set_ylim(-1, PLOT_HEIGHT + 1)
    plt.axis('off')


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