from pathlib import Path
from uuid import uuid4

from gdm import DistributionSystem, WindingEquipment, DistributionTransformerEquipment, SequencePair, ConnectionType, VoltageTypes
from gdm.quantities import PositiveVoltage, PositiveApparentPower
import pandas as pd

def build_regulator_models(xfmr_models: DistributionSystem):
    
    regulators = []
    data = pd.read_csv(Path(__file__).parent / "regulators.csv")

    # a : winding_models = None
    winding_models = list(xfmr_models.get_components(WindingEquipment))
    voltage_levels = set([x.nominal_voltage.to("volt").magnitude for x in winding_models])
    voltage_levels = sorted(voltage_levels)

    def find_closest_voltage_level(target):
        return min(voltage_levels, key=lambda x: abs(x - target))

    def find_closest_kva(target, kva_list):
        return min(kva_list, key=lambda x: abs(x - target))

    for i, reg_info in data.iterrows():
        v = int(reg_info["Voltage class  (kV)"] * 1000 * 1.732)
        c = reg_info["Load current (Amps)"]
        s = int(reg_info["Rated power (KVA)"])
        p = int(reg_info["Phases"])
        f = int(reg_info["Rated frequency (Hz) "])
        v_ln = int(reg_info["Voltage class  (kV)"] * 1000)

        reg_name = f"S{s}_V{v_ln}_P{p}_F{f}"

        winding_models = list(xfmr_models.get_components(WindingEquipment, filter_func=lambda x : x.nominal_voltage.to("volt").magnitude == find_closest_voltage_level(v)))
        kva_levels = set([x.rated_power.to("kilova").magnitude for x in winding_models])
        closest_kva = find_closest_kva(s, kva_levels)
        winding_models = [w for w in winding_models if w.rated_power.to("kilova").magnitude == closest_kva]
        
        print(f"Actual voltage {v} - Matched voltage {find_closest_voltage_level(v)}")
        print(f"Actual kva {s} - Matched kva {find_closest_kva(s, kva_levels)}")
        
        
        wdg = winding_models[0]
        wdg_1 = wdg.model_copy(
            update={
                'uuid': uuid4(),
                "num_phases" : p,
                "tap_positions" : [1.0] * p,
                "nominal_voltage":  PositiveVoltage(v, "volt"),
                "voltage_type" : VoltageTypes.LINE_TO_GROUND,
                "rated_power" : PositiveApparentPower(s, "kilova"),
                "total_taps" : 3,
                "min_tap_pu" : 0.90,
                "max_tap_pu" : 1.05,
                "connection_type" : ConnectionType.STAR,
            }
        )
        
        wdg_2 = wdg.model_copy(
            update={
                'uuid': uuid4(),
                "num_phases" : p,
                "tap_positions" : [1.0] * p,
                "nominal_voltage":  PositiveVoltage(v, "volt"),
                "voltage_type" : VoltageTypes.LINE_TO_GROUND,
                "rated_power" : PositiveApparentPower(s, "kilova"),
                "total_taps" : 33,
                "min_tap_pu" : 0.90,
                "max_tap_pu" : 1.05,
                "connection_type" : ConnectionType.STAR,
                
            }
        )

        xfmr = DistributionTransformerEquipment(
            name=reg_name,
            pct_no_load_loss=0.1,
            pct_full_load_loss=1,
            is_center_tapped=False,
            windings=[wdg_1, wdg_2],
            coupling_sequences=[SequencePair(0, 1)],
            winding_reactances=[4.0],
        )
        regulators.append(xfmr)
    return regulators