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

    rooms = {
        "Living": (20, 26),       # ~460
        "Balcony": (3, 5),        # ~80
        "Kitchen": (15, 19),        # ~250
        "NormalBedroom": (11, 14),  # ~230
        "MasterBedroom": (9, 13),  # ~240
        "Pooja": (2, 3),           # ~300
        "CombinedWC": (1, 3),      # ~100
        "Toilet": (2, 4),          # ~40
        "Bathroom": (3, 5),        
        "corridor": (4, 9)
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

    #layout generation
    WALL_THICKNESS = 0.5  
    layout = {}

    #liivng+pooja
    if PLOT_WIDTH > PLOT_HEIGHT:
        living_h_ratio = 0.45
    else:
        living_h_ratio = 0.65
 
    living_h = living_h_ratio*PLOT_HEIGHT
    living_w = rooms["Living"] / living_h
    living = Room(
        a1=Point(PLOT_WIDTH-living_w, PLOT_HEIGHT),
        a2=Point(PLOT_WIDTH, PLOT_HEIGHT),
        a3=Point(PLOT_WIDTH, PLOT_HEIGHT-living_h),
        a4=Point(PLOT_WIDTH-living_w, PLOT_HEIGHT-living_h),
        area=rooms["Living"]
    )
    layout["Living"] = living

    pooja_w = math.sqrt(rooms["Pooja"])
    pooja_h = pooja_w
    pooja = Room(
        a1=Point(PLOT_WIDTH-pooja_w, PLOT_HEIGHT),
        a2=Point(PLOT_WIDTH, PLOT_HEIGHT),
        a3=Point(PLOT_WIDTH, PLOT_HEIGHT-pooja_h),
        a4=Point(PLOT_WIDTH-pooja_w, PLOT_HEIGHT-pooja_h),
        area=rooms["Pooja"]
    )
    layout["Pooja"] = pooja

    #kitchen+balcony
    KB_area=rooms["Kitchen"]+rooms["Balcony"]
    KB_height=PLOT_HEIGHT-living_h
    KB_width=KB_area/KB_height

    kitchen_w=KB_width
    kitchen_h = rooms["Kitchen"] / kitchen_w
    kitchen = Room(
        a1=Point(PLOT_WIDTH-kitchen_w, PLOT_HEIGHT-living_h),
        a2=Point(PLOT_WIDTH, PLOT_HEIGHT-living_h),
        a3=Point(PLOT_WIDTH, PLOT_HEIGHT-living_h-kitchen_h),
        a4=Point(PLOT_WIDTH-kitchen_w, PLOT_HEIGHT-living_h-kitchen_h),
        area=rooms["Kitchen"]
    )
    layout["Kitchen"] = kitchen

    bal_w = KB_width
    bal_h = rooms["Balcony"] / bal_w
    balcony = Room(
        a1=Point(PLOT_WIDTH-bal_w, bal_h),
        a2=Point(PLOT_WIDTH, bal_h),
        a3=Point(PLOT_WIDTH, 0),
        a4=Point(PLOT_WIDTH-bal_w, 0),
        area=rooms["Balcony"]
    )
    layout["Balcony"] = balcony

    #masterbedroom
    MC_area=rooms["MasterBedroom"]+rooms["CombinedWC"]
    MC_width=PLOT_WIDTH-bal_w
    MC_height=MC_area/MC_width

    mb_w = MC_width
    mb_h = MC_area / mb_w
    master = Room(
        a1=Point(0, mb_h),
        a2=Point(mb_w, mb_h),
        a3=Point(mb_w, 0),
        a4=Point(0, 0),
        area=rooms["MasterBedroom"]
    )
    layout["MasterBedroom"] = master

    ratio_MC=MC_width/MC_height
    wc_h = math.sqrt(rooms["CombinedWC"] / ratio_MC)
    wc_w = wc_h * ratio_MC
    combined = Room(
        a1=Point(master.a1.x, master.a1.y),
        a2=Point(wc_w, master.a1.y),
        a3=Point(wc_w, master.a1.y-wc_h),
        a4=Point(0, master.a1.y-wc_h),
        area=rooms["CombinedWC"]
    )
    layout["CombinedWC"] = combined

    #normal bedroom
    nb_w= PLOT_WIDTH-living_w
    nb_h = rooms["NormalBedroom"] / nb_w
    normal = Room(
        a1=Point(0, PLOT_HEIGHT),
        a2=Point(living.a1.x, PLOT_HEIGHT),
        a3=Point(nb_w, PLOT_HEIGHT-nb_h),
        a4=Point(0, PLOT_HEIGHT-nb_h),
        area=rooms["NormalBedroom"]
    )
    layout["NormalBedroom"] = normal
 
    #bathroom
    bath_h = (PLOT_HEIGHT-mb_h-nb_h)*0.45
    bath_w = rooms["Bathroom"] / bath_h
    bathroom = Room(
        a1=Point(master.a1.x, master.a1.y+bath_h),
        a2=Point(bath_w, master.a1.y+bath_h),
        a3=Point(bath_w, master.a1.y),
        a4=Point(master.a1.x, master.a1.y),
        area=rooms["Bathroom"]
    )
    layout["Bathroom"] = bathroom
    
    #toilet
    toilet_h = (PLOT_HEIGHT-mb_h-nb_h)*0.55
    toilet_w = rooms["Toilet"] / toilet_h
    toilet = Room(
        a1=Point(0, normal.a4.y),
        a2=Point(toilet_w, normal.a4.y),
        a3=Point(toilet_w, bathroom.a1.y),
        a4=Point(0, bathroom.a1.y),
        area=rooms["Toilet"]
    )
    layout["Toilet"] = toilet
   
    #helping functions
    def draw_door(ax, cx, cy, r, t1, t2):
        ax.add_patch(Arc((cx, cy), r*2, r*2, theta1=t1, theta2=t2, linewidth=1.5, color="black", zorder=12))
        ax.plot([cx, cx + r * math.cos(math.radians(t1))], [cy, cy + r * math.sin(math.radians(t1))], color="black", lw=1.5, zorder=13)
        ax.plot([cx, cx + r * math.cos(math.radians(t2))], [cy, cy + r * math.sin(math.radians(t2))], color="black", lw=1.0, ls="--", zorder=11)

    def draw_opening_v(ax, x, yc, w):
        ax.plot([x, x], [yc - w/2, yc + w/2], lw=4, color="white", zorder=11, solid_capstyle='butt')

    def draw_opening_h(ax, xc, y, w):
        ax.plot([xc - w/2, xc + w/2], [y, y], lw=4, color="white", zorder=11, solid_capstyle='butt')

    # --- UPDATED: Double Wall Logic from Code 2 ---
    def draw_double_wall(ax, room):
        x, y = room.a4.x, room.a4.y
        w, h = room.a2.x - room.a1.x, room.a1.y - room.a4.y
        ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor="black", lw=1.5, zorder=5))
        ax.add_patch(Rectangle((x + WALL_THICKNESS, y + WALL_THICKNESS),
                             w - 2*WALL_THICKNESS, h - 2*WALL_THICKNESS,
                             fill=True, facecolor='white', edgecolor="black",
                             alpha=0.6, lw=0.8, zorder=4))

  
    def draw_furniture(ax, room_name, room):
        fabric_color = '#94a3b8'
        detail_color = '#475569'
        wood_color = '#b5835a'
        
        # Calculate local room dims
        rw = room.a2.x - room.a1.x
        rh = room.a1.y - room.a4.y

        if room_name == "Living":
            sofa_x = room.a4.x + WALL_THICKNESS
            # Adjust y base relative to the room's bottom
            sofa_y_base = room.a4.y + (rh-WALL_THICKNESS)*0.4
            
            # Use local width/height for proportions
            v_h = (rh-WALL_THICKNESS)*0.6 - rw*0.18
            v_w = rw*0.18
            h_l = (rw-pooja_w)*0.8 

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
            ax.add_patch(Rectangle((room.a2.x - rw*0.6, room.a1.y - rh + WALL_THICKNESS), (rw*0.35), rh*0.1, color=wood_color, ec=detail_color, zorder=20))
        
        elif room_name == "Kitchen":
            # Counter
            ax.add_patch(Rectangle((room.a2.x - rw*0.15- WALL_THICKNESS, room.a3.y + WALL_THICKNESS), (rw*0.15), (rh-2*WALL_THICKNESS), color='#e2e8f0', ec='#94a3b8', zorder=20))
            
            # Stove
            stove_x, stove_y = room.a2.x - rw*0.15, room.a4.y + rh/2 - 1.5
            ax.add_patch(Rectangle((stove_x, stove_y), rw*0.1, rh*0.3, color='#334155', zorder=21))
            for i in range(3):
                ax.add_patch(Circle((stove_x + rw*0.05, stove_y + rh*0.04 + i*(rh*0.25/3)), rh*0.025, color='black', ec='white', lw=0.3, zorder=22))
            
            # Table
            t_width, t_height = rw*0.3, rh*0.2 
            t_center_x, t_center_y = room.a4.x +WALL_THICKNESS+(t_height+t_width)*0.5, room.a4.y + WALL_THICKNESS + t_height*0.5
            ax.add_patch(Rectangle((t_center_x - t_width/2, t_center_y - t_height/2), t_width, t_height, color='#8d6e63', ec='#5d4037', lw=1.5, zorder=20))
            
            # Chairs
            chair_dist = t_height/2 + t_height*0.25  
            chair_positions = [(-t_width/4, chair_dist), (t_width/4, chair_dist), (-t_width/2 - t_height*0.25, 0), (t_width/2 + t_height*0.25, 0)]
            for cx_off, cy_off in chair_positions:
                ax.add_patch(Circle((t_center_x + cx_off, t_center_y + cy_off), t_height*0.25, color='#5d4037', zorder=20))
        
        elif "Bedroom" in room_name:
            # Determine size based on room dims
            bed_w, bed_h = min(rw*0.5,12), min(rh*0.5,9)
            
            # Align bed
            if room_name == "MasterBedroom":
                # Bottom-Left logic
                bx = room.a4.x + WALL_THICKNESS
                by = room.a4.y + WALL_THICKNESS
            else:
                # Top-Left logic (Original)
                bx = room.a4.x + WALL_THICKNESS
                by = room.a1.y - bed_h - 2*WALL_THICKNESS
            
            ax.add_patch(Rectangle((bx, by), bed_w, bed_h, color='#cbd5e1', ec=detail_color, lw=1, zorder=20))
            ax.add_patch(Rectangle((bx, by), 0.5, bed_h, color=detail_color, zorder=21)) # Headboard
            
            # Pillows
            for py in [by + bed_h*0.1, by + bed_h*0.6]:
                ax.add_patch(Rectangle((bx + 0.8, py), bed_w*0.15, bed_h*0.3, color='white', ec='gray', lw=0.5, zorder=22))
            ax.plot([bx + 3, bx + 3], [by, by + bed_h], color=detail_color, lw=0.8, ls='--', zorder=21)
            
            # Wardrobes
            #if room_name == "MasterBedroom":
                ## Right Wall Wardrobe
                #tx, ty = room.a2.x - 2.5 - WALL_THICKNESS, room.a3.y + 2
               # if tx > bx + bed_w: # Only if space exists
                #    ax.add_patch(Rectangle((tx, ty), 2.5, 6, color=wood_color, ec='#5c4033', lw=1, zorder=20))
                    #ax.add_patch(Rectangle((tx + 0.5, ty + 2), 1.5, 2, color='#334155', zorder=21))
                    #ax.add_patch(Circle((tx - 1.2, ty + 3), 0.8, color='#475569', zorder=20))
            #elif room_name == "NormalBedroom":
                # Bottom Wall Wardrobe (relative to room)
                #tx, ty = room.a2.x - 6 - WALL_THICKNESS, room.a4.y + WALL_THICKNESS
                #ax.add_patch(Rectangle((tx, ty), 6, 2.5, color=wood_color, ec='#5c4033', lw=1, zorder=20))
                
        elif room_name == "Bathroom":
            ax.add_patch(Rectangle((room.a2.x-rw*0.9 , room.a4.y + rh*0.2), rw*0.5, rh*0.5, color='#f1f5f9', ec='black', zorder=20))
            ax.add_patch(Ellipse((room.a2.x - rw*0.65, room.a4.y + rh*0.45), rw*0.4, rh*0.4, color='white', ec='#3b82f6', lw=0.8, zorder=21))
        
        elif room_name in ["Toilet", "CombinedWC"]:
            tank_height = 0.8
            ax.add_patch(Rectangle((room.a4.x +WALL_THICKNESS, room.a1.y - WALL_THICKNESS - tank_height), rw*0.2, tank_height, color='white', ec='gray', zorder=21))
            ax.add_patch(Ellipse((room.a4.x + WALL_THICKNESS + rw*0.1, room.a1.y - WALL_THICKNESS - tank_height-rh*0.2), rw*0.15, rh*0.5, color='white', ec='gray', zorder=20))


    #plotting
    fig, ax = plt.subplots(figsize=(10, 14))

    #wooden background (From Code 2)
    wood_base = np.full((100, 100, 3), [0.8, 0.7, 0.5])
    noise = np.random.normal(0, 0.02, (100, 100, 3))
    wood_texture = np.clip(wood_base + noise, 0, 1)
    for i in range(0, 100, 5): wood_texture[:, i:i+2, :] -= 0.05
    ax.imshow(wood_texture, extent=[-2, PLOT_WIDTH + 2, -2, PLOT_HEIGHT + 2], aspect='auto', zorder=0)

    # Main Plot Outer Border
    ax.add_patch(plt.Rectangle((0,0), PLOT_WIDTH, PLOT_HEIGHT, fill=False, linewidth=4, edgecolor='black', zorder=4))

    # Draw Rooms using new Logic
    for name, room in layout.items():
        draw_double_wall(ax, room)
        draw_furniture(ax, name, room)
        
        # Text labels (Center)
        w_curr = room.a2.x - room.a1.x
        h_curr = room.a1.y - room.a4.y
        ax.text(room.a4.x + w_curr/2, room.a4.y + h_curr/2, name.replace("_", " "), ha="center", va="center",
                fontsize=8, fontweight='bold', zorder=25,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    #OPENINGS
    draw_opening_h(ax, PLOT_WIDTH-kitchen_w-(living_w-kitchen_w)*0.5,PLOT_HEIGHT-living_h, min(4,living_w-kitchen_w)) #living-door
    draw_opening_v(ax, (PLOT_WIDTH-kitchen_w), mb_h+(kitchen_h-mb_h)*0.5,min(4,kitchen_h-mb_h) )#kitchen-door

    # For Toilet (left wall)
    toilet_room = layout["Toilet"]
    toilet_center_y = toilet_room.a4.y + (toilet_room.a1.y - toilet_room.a4.y) / 2
    draw_opening_v(ax, toilet_room.a4.x, toilet_center_y, 1.8) #toilet

    # For Bathroom (left wall)
    bathroom_room = layout["Bathroom"]
    bathroom_center_y = bathroom_room.a4.y + (bathroom_room.a1.y - bathroom_room.a4.y) / 2
    draw_opening_v(ax, bathroom_room.a4.x, bathroom_center_y, 1.8) #bathroom
    draw_opening_h(ax, (mb_w*0.5), 0, 4) #master
    draw_opening_v(ax, PLOT_WIDTH, kitchen_h*0.9, 5) #kitchen
    draw_opening_h(ax,(nb_w*0.5), PLOT_HEIGHT, 5) #BED-NORMAL
    draw_opening_h(ax,PLOT_WIDTH-living_w*0.5 , PLOT_HEIGHT, 5) #living

    #Doors & Openings 
    D_RAD = 1.7
    draw_door(ax, mb_w*0.7,mb_h , D_RAD-0.5, 180, 270) #master bedroom
    draw_door(ax, toilet_w, PLOT_HEIGHT - nb_h - toilet_h*0.5, D_RAD-1, 180, 270) #toilet
    draw_door(ax, bath_w, mb_h + 0.5*bath_h, D_RAD-1, 180, 270)  #bathroom
    draw_door(ax, nb_w*0.7, PLOT_HEIGHT - nb_h, D_RAD-0.5, 90, 180)  #normal bed

    draw_door(ax, PLOT_WIDTH , (PLOT_HEIGHT-living_h*0.5), D_RAD-0.5, 180, 270)   #entry door
    draw_door(ax, mb_w+bal_w*0.6 , bal_h, D_RAD-1, 0, 90) #balcony
    draw_door(ax, wc_w , mb_h-wc_h*0.5, D_RAD-1, 180, 270) #master_toilet
    draw_door(ax, PLOT_WIDTH-pooja_w, PLOT_HEIGHT-pooja_h*0.5, D_RAD-1, 0, 90) #pooja room


    ax.set_aspect("equal")
    ax.set_xlim(-1, PLOT_WIDTH+1)
    ax.set_ylim(-1, PLOT_HEIGHT+1)
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