from pathlib import Path
from uuid import uuid4
import math

from gdm.distribution.equipment import SolarEquipment, InverterEquipment
from gdm.quantities import PositiveApparentPower, PositiveActivePower
from gdm.distribution.enums import VoltageTypes
from gdm.distribution.common import Curve
from gdm.quantities import PositiveVoltage
from infrasys import Component
import pandas as pd
import numpy as np


def build_pv_and_inverter_models()-> list[Component]:

    inverter_file = Path(__file__).parent / "adr-library-cec-inverters-2019-03-05.csv"
    pvs_and_inverters = []
    df = pd.read_csv(inverter_file)
    for idx, row_data in df.iterrows():
        if idx > 1:
            try:
                cooficients = row_data['ADRCoefficients'].replace('[', '').replace(']', '').replace(' ', ',').split(',')
                v_ac_volts = float(row_data['Vac'])
                cooficients = [float(c) for c in cooficients if c != '']
                b_0_0, b_1_0, b_2_0, b_0_1, b_1_1, b_2_1, b_0_2, b_1_2, b_2_2 = cooficients
                v_in = 1
                p_in = np.arange(0, 1.2, 0.05)
                p_loss = ( 
                    (b_0_0 + b_0_1 * (v_in - 1) + b_0_2 * (1 / v_in - 1)) + 
                    (b_1_0 + b_1_1 * (v_in - 1) + b_1_2 * (1 / v_in - 1)) * p_in  +
                    (b_2_0 + b_2_1 * (v_in - 1) + b_2_2 * (1 / v_in - 1)) * np.square(p_in)
                )
                eff = (p_in - p_loss) / p_in * 100
                eff = np.clip(eff, a_min=0, a_max=100)
                p_ac_max = float(row_data['Pacmax'])
                inverter = InverterEquipment(
                    uuid=uuid4(),
                    name=row_data['Name'],
                    rated_apparent_power=PositiveApparentPower(p_ac_max, "va"),
                    rise_limit=None,
                    fall_limit=None,
                    eff_curve=Curve(
                        curve_x= PositiveActivePower(p_in * p_ac_max , "watts"),
                        curve_y= eff,
                    ),
                    cutout_percent = float(row_data['MPPTLow']) / p_ac_max * 100 if float(row_data['MPPTLow']) > 0 else 0,
                    cutin_percent = float(row_data['MPPTLow']) / p_ac_max * 100 if float(row_data['MPPTLow']) > 0 else 0,
                    dc_to_ac_efficiency = max(eff) / len(eff)

                )
                solar = SolarEquipment(
                    uuid=uuid4(),
                    name=str(uuid4()),
                    rated_power=PositiveActivePower(p_ac_max, "watts"),
                    resistance = float(0),
                    reactance = float(0),
                    rated_voltage = PositiveVoltage(v_ac_volts, "volt"),
                    voltage_type=VoltageTypes.LINE_TO_LINE,
                )


                pvs_and_inverters.append(inverter)
                pvs_and_inverters.append(solar)
            except:
                pass
    return pvs_and_inverters