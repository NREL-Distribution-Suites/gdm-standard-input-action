from pathlib import Path

from gdm import ConnectionType, WindingEquipment, DistributionTransformerEquipment, SequencePair, VoltageTypes, DistributionSystem
from gdm.quantities import PositiveVoltage, PositiveApparentPower
from infrasys import Component
import pandas as pd

def build_three_phase_xfmr()-> list[Component]:
    transformers = []
    # three_wire = [
    #     "4160",
    #     "4800",
    #     "6900",
    #     "13800",
    #     "23000",
    #     "34500",
    # ]

    four_wire = [
        "4160Y/2400",
        "12470Y/7200",
        "13200Y/7620",
        "13800Y/7970",
        "24940Y/14400",
        "34500Y/19920",
    ]

    p3_imp_data = pd.read_csv(Path(__file__).parent / 'three_phase_impedance.csv')
    p3_volt_data = pd.read_csv(Path(__file__).parent / 'three_phase_voltage_levels.csv')


    for _, row in p3_imp_data.iterrows():
        kva = row['kVA']
        #z_pct = row['%IZ']
        r_pct = row['%IR']
        x_pct = row['%IX']
        #xr_ratio = row['X/R Ratio']
        loss_no_load = float(row['No load loss - W'].replace(",", ""))
        loss_full_load = float(row['Full load loss -W'].replace(",", ""))
        taps = 5
        max_pu = 1.05
        min_pu = 0.95
        #xfmr_type = row['Type']

        p3_volt_data_filtered = p3_volt_data[p3_volt_data["kva"] == kva]
        for _, voltage_data in p3_volt_data_filtered.iterrows():

            v_sec = voltage_data["sec_voltage"]
            conn_sec = ConnectionType.STAR if "Y" in v_sec else ConnectionType.DELTA 
            v_sec = int(v_sec.split("Y")[0].replace("V", ""))
            for v_pri in four_wire:
                conn_pri = ConnectionType.STAR if "Y" in v_pri else ConnectionType.DELTA 
                v_pri = int(v_pri.split("Y")[0].replace("V", ""))
                hv_kv_min = voltage_data["hv_kv_min"]
                hv_kv_max = voltage_data["hv_kv_max"]
                try:
                    hv_kv_min = float(hv_kv_min) * 1000
                    hv_kv_max = float(hv_kv_max) * 1000
                    if v_pri > hv_kv_min and v_pri < hv_kv_max:
                        kva_xfmr = int(kva.replace(",", ""))
                        loss_no_load_pct = (loss_no_load / 1000.0) / kva_xfmr * 100.0
                        loss_full_load_pct = (loss_full_load / 1000.0) / kva_xfmr * 100.0
                        
                        c_hv=  "D" if conn_pri==ConnectionType.DELTA else "Y"
                        c_lv=  "D" if conn_sec==ConnectionType.DELTA else "Y"
                        xfmr_name = f"3p_{kva_xfmr}kva_{v_pri}{c_hv}_{v_sec}{c_lv}"
           
                        wdg_hv = WindingEquipment(
                            resistance=r_pct /2,
                            is_grounded=False,
                            nominal_voltage=PositiveVoltage(v_pri, "volt"),
                            rated_power=PositiveApparentPower(kva_xfmr, "kilova"),
                            connection_type=conn_pri,
                            num_phases=3,
                            tap_positions=[1.0, 1.0, 1.0],
                            voltage_type=VoltageTypes.LINE_TO_LINE,
                        )
                        
                        wdg_lv = WindingEquipment(
                            resistance=r_pct / 2,
                            is_grounded=False,
                            nominal_voltage=PositiveVoltage(v_sec, "volt"),
                            rated_power=PositiveApparentPower(kva_xfmr, "kilova"),
                            connection_type=conn_sec,
                            num_phases=3,
                            tap_positions=[1.0, 1.0, 1.0],
                            voltage_type=VoltageTypes.LINE_TO_LINE,
                            total_taps=taps,
                            max_tap_pu=max_pu,
                            min_tap_pu=min_pu
                        )
                        
                        xfmr = DistributionTransformerEquipment(
                            name = xfmr_name,
                            is_center_tapped=False,
                            pct_full_load_loss=loss_full_load_pct,
                            pct_no_load_loss=loss_no_load_pct,
                            windings=[wdg_hv, wdg_lv],
                            coupling_sequences=[SequencePair(0, 1)],
                            winding_reactances=[x_pct],
                        )    
                        
                        transformers.append(xfmr)
                    
                except Exception as e:
                    ...
    return transformers
