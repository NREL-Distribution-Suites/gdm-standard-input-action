from pathlib import Path

from gdm.distribution.equipment import (
    PhaseCapacitorEquipment,
    CapacitorEquipment,
)
from gdm.distribution.enums import (
    ConnectionType,
    VoltageTypes,
)
from gdm.quantities import PositiveReactivePower, PositiveResistance, PositiveVoltage
import pandas as pd


def losses_watts(kvar):
    return 0.12 * kvar


def build_capacitor_models() -> list[CapacitorEquipment]:
    capacitors = []
    data = pd.read_csv(Path(__file__).parent / "capacitors.csv")
    for _, cap_info in data.iterrows():
        q = int(cap_info["kVAr"])
        v = int(cap_info["kV"] * 1000)
        f = cap_info["Hz"]
        p = cap_info["Phases"]
        b = cap_info["Bushing"]
        c = cap_info["Amp"]
        l = losses_watts(q / p)
        r = l / c**2

        cap_name = f"Q{q}_V{v}_P{p}_B{b}_F{f}"
        phs_cap_equip = []
        for i in range(p):
            phs_cap_equip.append(
                PhaseCapacitorEquipment(
                    name=f"{cap_name}_{i}",
                    rated_reactive_power=PositiveReactivePower(q / p, "kvar"),
                    resistance=PositiveResistance(r, "ohm"),
                    num_banks=1,
                    num_banks_on=1,
                )
            )

        capacitor = CapacitorEquipment(
            name=cap_name,
            phase_capacitors=phs_cap_equip,
            connection_type=ConnectionType.STAR,
            rated_voltage=PositiveVoltage(v, "volt"),
            voltage_type=VoltageTypes.LINE_TO_GROUND,
        )
        capacitors.append(capacitor)
    return capacitors
