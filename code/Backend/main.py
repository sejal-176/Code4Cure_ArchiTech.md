import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyuploadcare import Uploadcare 

# import layout generators
from layouts import bhk2_N, bhk1_E, bhk1_N, bhk2_E, bhk2_nm_E, bhk2_nm_N, bhk3_new,bhk3_m2n_E, bhk3_m2n_N, bhk3_mgn_E, bhk3_mgn_N

app = FastAPI()

UPLOADCARE_PUBLIC_KEY = '42e943707dcefc0855f3'
UPLOADCARE_SECRET_KEY = 'fbf4db02cda3784a5660'
uploadcare = Uploadcare(public_key=UPLOADCARE_PUBLIC_KEY, secret_key=UPLOADCARE_SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LayoutRequest(BaseModel):
    plot_height: int
    plot_width: int
    entrance_type: str | None = None
    room_type: str
    config: str | None = None


@app.post("/generator")
def generate_layout(data: LayoutRequest):
    plot_height = data.plot_height
    plot_width = data.plot_width
    entrance_type = data.entrance_type.lower()
    room_type = data.room_type.lower()
    config = data.config.lower() 

    try:
        if(0.4<=(plot_height/plot_width)<2 or 1.5>(plot_width/plot_height)>= 0.5):
            if room_type == "1bhk":
                if entrance_type == "north":
                    result = bhk1_N.generate(plot_height, plot_width)
                else:
                    result = bhk1_E.generate(plot_height, plot_width)

            elif room_type == "2bhk":
                if entrance_type == "north":
                    if config == "2normal":
                        result = bhk2_N.generate(plot_height, plot_width)
                    else:
                        result = bhk2_nm_N.generate(plot_height, plot_width)
                else:
                    if config == "2normal":
                        result = bhk2_E.generate(plot_height, plot_width)
                    else:
                        if plot_width>plot_height:
                            result = bhk2_nm_E.generate(plot_height, plot_width)
                        
            
            elif room_type == "3bhk":
                if entrance_type == "east":
                    if config == "1master2normal":
                        result = bhk3_m2n_E.generate(plot_height, plot_width)
                    else:
                        if plot_width>plot_height:
                            result = bhk3_mgn_E.generate(plot_height, plot_width)
                        else:
                            result = bhk3_new.generate(plot_height, plot_width) 
                
                else:
                    if config == "1master2normal":
                        result = bhk3_m2n_N.generate(plot_height, plot_width)  
                    else:              
                        result = bhk3_mgn_N.generate(plot_height, plot_width)
            
            else:
                return {"error": "Invalid room type"}
        
        image_path = result["image_path"]
        report_path = result.get("report_path")
        layout_id = result.get("layout_id")
        
        full_report = result.get("full_report")

    except Exception as e:
        print(f"Generation failed: {e}")
        return {"error": f"Layout generation failed: {str(e)}"}
    
    time.sleep(1) 
    
    try:
        if not os.path.exists(image_path):
            print(f"Error: File not found at {image_path}")
            return {"error": "File not found"}

        with open(image_path, 'rb') as file_object:
            ucare_file = uploadcare.upload(file_object)
            ucare_file.store()
            
            # --- WAIT FOR CDN READINESS ---
            attempts = 0
            while not ucare_file.is_ready and attempts < 10:
                time.sleep(0.5)
                ucare_file.update_info() 
                attempts += 1
            
        cloud_url = f"https://5ririmndgn.ucarecd.net/{ucare_file.uuid}/"
        
        # Cleanup local files
        if os.path.exists(image_path): os.remove(image_path)
        if report_path and os.path.exists(report_path): os.remove(report_path)
        
        print(f"File Ready on CDN: {cloud_url}")
        
        # --- 3. RETURN DATA TO FRONTEND ---
        return {
            "status": "success", 
            "image_url": cloud_url,
            "layout_id": layout_id,
            "full_report": full_report  # Pass the complete technical data
        }
    except Exception as e:
        print(f"Upload failed: {e}")
        return {"error": str(e)}