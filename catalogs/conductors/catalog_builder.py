from pathlib import Path

from infrasys import Component
from gdm import ConcentricCableEquipment, BareConductorEquipment
from gdm.quantities import PositiveDistance, PositiveCurrent, PositiveResistancePULength, PositiveVoltage
import pandas as pd
import numpy as np




def build_conductor_models()-> list[Component]:
    conductors_and_cables = []
    xlxs_path = Path(__file__).parent / "conductor_data.xlsx"

    data = pd.read_excel(xlxs_path, sheet_name= 4)
    for i, conductor_info in data.iterrows():
        
        cond_name = conductor_info["Material"] + "_" + str(conductor_info["Size"]) + "_" + str(conductor_info["Stranding"]) 

        r_dc = conductor_info["RES Ω/mile"] * 0.8
        r_ac = conductor_info["RES Ω/mile"]
        gmr = conductor_info["GMR Feet"]
        ampacity = conductor_info["Amps"]
        diam = conductor_info["DIAM Inches"]
        
        conductor = BareConductorEquipment(
            name = cond_name,
            conductor_diameter=PositiveDistance(diam, "in"),
            conductor_gmr=PositiveDistance(gmr, "ft"),
            ampacity=PositiveCurrent(ampacity, "ampere"),
            ac_resistance=PositiveResistancePULength(r_ac, "ohm/m"),
            dc_resistance=PositiveResistancePULength(r_dc, "ohm/m"),
            emergency_ampacity=PositiveCurrent(ampacity, "ampere"),
        )
        conductors_and_cables.append(conductor)


    conductor_data = pd.read_excel(xlxs_path, sheet_name= 0)
    for i, conductor_info in conductor_data.iterrows():
        
        n = conductor_info["Type"] + "_" + conductor_info["AWG"] 
        cond_name = conductor_info["Code"] if str(conductor_info["Code"]) != "nan" else n
        r_dc = conductor_info["Resistance-  dc 20 °C (Ω/kft)"] * 5.28
        r_ac = conductor_info["Resistance-  ac 75 °C (Ω/kft)"] * 5.28
        gmr = conductor_info["GMR -ft"]
        ampacity = conductor_info["Ampacity (amps)"]
        diam = conductor_info["Conductor Diameter (in)"]

        if str(gmr) != "nan":
            conductor = BareConductorEquipment(
                name = cond_name,
                conductor_diameter=PositiveDistance(diam, "in"),
                conductor_gmr=PositiveDistance(gmr, "ft"),
                ampacity=PositiveCurrent(ampacity, "ampere"),
                ac_resistance=PositiveResistancePULength(r_ac, "ohm/m"),
                dc_resistance=PositiveResistancePULength(r_dc, "ohm/m"),
                emergency_ampacity=PositiveCurrent(ampacity, "ampere"),
            )
            conductors_and_cables.append(conductor)
        
    acsr_cables =conductor_data#[conductor_data["Type"] == "ACSR"]


    cable_data = pd.read_excel(xlxs_path, sheet_name= 1)
    for i, cable_info in cable_data.iterrows():
        cond_name = cable_info["Code"]
        awg_conductor = cable_info["AWG"]
        n_strands_conductor = cable_info["Stranding"]
        insulation_thickness_inches = cable_info["Insulation Thickness (inches)"]
        awg_neutral = cable_info["AWG -neutral"]
        n_strands_neutral = cable_info["Strands - neutral"]
        cable_diameter = cable_info["Outside Diameter conductor (inches)"] * 2
        xlp_weight  = cable_info["XLP (lbs/kft)"]
        poly_weight = cable_info["POLY (lbs/kft)"]
        xlp_ampacity = cable_info["Ampacity - XLP"]
        poly_ampacity = cable_info["Ampacity - POLY"]
        cable_type = cable_info["Type"]

        if str(n_strands_neutral) != "nan":
            
            conductor = acsr_cables[acsr_cables["AWG"] == awg_conductor]
            neutral = acsr_cables[acsr_cables["AWG"] == awg_neutral]
                    
            if conductor.empty:
                awg_conductor = awg_conductor + ".0"
                conductor = acsr_cables[acsr_cables["AWG"] == awg_conductor]

            if neutral.empty:
                awg_neutral = awg_neutral + ".0"
                neutral = acsr_cables[acsr_cables["AWG"] == awg_neutral]

            if not conductor.empty and not neutral.empty:
                conductor = conductor.loc[conductor.index[0]]
                neutral = neutral.loc[neutral.index[0]]
                
                cond_diam = conductor["Conductor Diameter (in)"]
                insulation_diameter = (cond_diam + insulation_thickness_inches * 2) * 1.001
                n_strands_neutral = sum([int(x) for x in n_strands_neutral.split("/")])
                if neutral["Steel Core (Inches)"] > 0:
                    
                    cable = ConcentricCableEquipment(
                        name= cond_name + "_xlp",
                        
                        cable_diameter= PositiveDistance(cable_diameter, "inch"),
                        
                        phase_ac_resistance= PositiveResistancePULength(conductor["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
                        conductor_diameter= PositiveDistance(conductor["Conductor Diameter (in)"], "inch"),
                        conductor_gmr= PositiveDistance(conductor["GMR -ft"], "inch"),
                        
                        strand_ac_resistance= PositiveResistancePULength(neutral["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
                        num_neutral_strands=int(n_strands_neutral),
                        strand_diameter= PositiveDistance(neutral["Steel Core (Inches)"], "inch"),
                        strand_gmr= PositiveDistance(neutral["GMR -ft"], "inch"),
                        
                        insulation_thickness= PositiveDistance(insulation_thickness_inches, "inch"),
                        insulation_diameter= PositiveDistance(insulation_diameter, "inch"),
                        
                        emergency_ampacity= PositiveCurrent(xlp_ampacity * 1.10, "ampere"),
                        ampacity= PositiveCurrent(xlp_ampacity, "ampere"),
                        rated_voltage= PositiveVoltage(600, "volt"),
                    )
                    conductors_and_cables.append(cable)
                    try:
                        cable = ConcentricCableEquipment(
                            name= cond_name + "_polt",
                            
                            cable_diameter= PositiveDistance(cable_diameter, "inch"),
                            
                            phase_ac_resistance= PositiveResistancePULength(conductor["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
                            conductor_diameter= PositiveDistance(conductor["Conductor Diameter (in)"], "inch"),
                            conductor_gmr= PositiveDistance(conductor["GMR -ft"], "inch"),
                            
                            strand_ac_resistance= PositiveResistancePULength(neutral["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
                            num_neutral_strands=int(n_strands_neutral),
                            strand_diameter= PositiveDistance(neutral["Steel Core (Inches)"], "inch"),
                            strand_gmr= PositiveDistance(neutral["GMR -ft"], "inch"),
                            
                            insulation_thickness= PositiveDistance(insulation_thickness_inches, "inch"),
                            insulation_diameter= PositiveDistance(insulation_diameter, "inch"),
                            
                            emergency_ampacity= PositiveCurrent(poly_ampacity * 1.10, "ampere"),
                            ampacity= PositiveCurrent(poly_ampacity, "ampere"),
                            rated_voltage= PositiveVoltage(600, "volt"),
                        )
                        conductors_and_cables.append(cable)
                    except:
                        pass
                        
    cable_data_2 = pd.read_excel(xlxs_path, sheet_name=2)

    for i, cable_info_2 in cable_data_2.iterrows():
        conductor = cable_info_2["Conductor "]
        kv = cable_info_2["Voltage level"]
        nphases = cable_info_2["Number of phases"].lower().replace(" ", "_")
        conc_neutral = cable_info_2["Concentric Neutral "]
        material = cable_info_2["Material"].lower().replace(" ", "_")
        insulation_thickness_inches = cable_info_2["Insulation Thickness (mils) "] / 1000.0
        diameter_conductor = cable_info_2["Conductor Diameter (in)"]
        diameter_insulation = cable_info_2[" Insulation Diameter (in)"]
        diameter_insulation_shield = cable_info_2["Insulation Shield Diameter (in) "]  
        diameter_jacket = cable_info_2["Jacket Diameter (in) "]
        ampacity = cable_info_2["Ampacity (Amps) - duct"]

        cond_name = conductor + "_" + nphases + "_" + kv + "_" + conc_neutral + "_" + material
        
        kv = int(kv.replace("KV", ""))
        conductor_type = conductor.split("_")[0]
        n_strands, neutral_guage = conc_neutral.split("-")
        neutral_guage = neutral_guage.replace("#", "")
        n_strands = int(n_strands)
        nphases = 1 if nphases == "single_phase" else 3
        
        conductor = acsr_cables[acsr_cables["AWG"] == conductor_type]
        neutral = acsr_cables[acsr_cables["AWG"] == neutral_guage]
            
        if conductor.empty:
            conductor_type = conductor_type + ".0"
            conductor = acsr_cables[acsr_cables["AWG"] == conductor_type]
        
        if neutral.empty:
            awg_neutral = awg_neutral + ".0"
            neutral = acsr_cables[acsr_cables["AWG"] == neutral_guage]
        
        if not conductor.empty and not neutral.empty:
            conductor = conductor.loc[conductor.index[0]]
            neutral = neutral.loc[neutral.index[0]]

        cable = ConcentricCableEquipment(
            name= cond_name,
            
            cable_diameter= PositiveDistance(diameter_jacket, "inch"),
            
            phase_ac_resistance= PositiveResistancePULength(conductor["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
            conductor_diameter= PositiveDistance(diameter_conductor, "inch"),
            conductor_gmr= PositiveDistance(conductor["GMR -ft"], "inch"),
            
            strand_ac_resistance= PositiveResistancePULength(neutral["Resistance-  ac 75 °C (Ω/kft)"], "ohm/kilofeet"),
            strand_diameter= PositiveDistance(neutral["Conductor Diameter (in)"]/10.0, "inch"),
            strand_gmr= PositiveDistance(neutral["GMR -ft"], "inch"),
            num_neutral_strands=int(n_strands),
            
            insulation_thickness= PositiveDistance(insulation_thickness_inches, "inch"),
            insulation_diameter= PositiveDistance(diameter_insulation, "inch"),
            
            emergency_ampacity= PositiveCurrent(ampacity * 1.10, "ampere"),
            ampacity= PositiveCurrent(ampacity, "ampere"),
            rated_voltage= PositiveVoltage(kv, "kilovolt"),
        )
        conductors_and_cables.append(cable)
    return conductors_and_cables
