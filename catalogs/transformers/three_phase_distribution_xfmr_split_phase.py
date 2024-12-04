from pathlib import Path

from gdm import ConnectionType, WindingEquipment, DistributionTransformerEquipment, SequencePair, VoltageTypes, DistributionSystem
from gdm.quantities import PositiveVoltage, PositiveApparentPower
import pandas as pd



def build_split_phase_xfmr():
    xfmrs = []

    xfmr_data = pd.read_csv(Path(__file__).parent /'three_phase_distribution_xfmr_split_phase.csv')

    for _, row in xfmr_data.iterrows():

        xfmr_name = row["SKU"]
        kva = row["KVA"]
        no_load_loss = row["No load loss [kW]"] / kva * 100.0
        full_load_loss = row["Full load loss [kW]"] / kva * 100.0
        v_sec = int(row["Secondary Voltage"].split("/")[0])
        c_sec = ConnectionType.STAR
        v_pri = row["Primary Voltage"].split("GrdY/")
        c_pri = ConnectionType.STAR
        
        z = row["%Z"]
        xr_ratio = row["X/R"]
        
        r =  (z**2 / (1 +  xr_ratio**2))**0.5
        x  = r * xr_ratio
        v_pri = [int(v.replace("Y", "")) for v in v_pri]
   
        wdg_hv = WindingEquipment(
            resistance= r / 2,
            is_grounded=True,
            nominal_voltage=PositiveVoltage(v_pri[0], "volt"),
            rated_power=PositiveApparentPower(kva, "kilova"),
            connection_type=c_pri,
            num_phases=1,
            tap_positions=[1.0],
            voltage_type=VoltageTypes.LINE_TO_LINE,
        )
        
        wdg_lv = WindingEquipment(
            resistance= r / 2,
            is_grounded=False,
            nominal_voltage=PositiveVoltage(v_sec, "volt"),
            rated_power=PositiveApparentPower(kva, "kilova"),
            connection_type=c_sec,
            num_phases=1,
            tap_positions=[1.0],
            voltage_type=VoltageTypes.LINE_TO_LINE,
        )
        
        xfmr = DistributionTransformerEquipment(
            name = xfmr_name,
            is_center_tapped=True,
            pct_full_load_loss=full_load_loss,
            pct_no_load_loss=no_load_loss,
            windings=[wdg_hv, wdg_lv],
            coupling_sequences=[SequencePair(0, 1)],
            winding_reactances=[x],
        )    
        
        xfmrs.append(xfmr)
    return xfmrs
                
