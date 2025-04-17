from pathlib import Path

from gdm.distribution.common import SequencePair
from gdm.distribution.equipment import (
    DistributionTransformerEquipment,
    WindingEquipment,
)
from gdm.distribution.enums import (
    ConnectionType,
    VoltageTypes,
)
from gdm.quantities import PositiveVoltage, PositiveApparentPower
import pandas as pd
import numpy as np


class Model:
    def __init__(self):
        self.base_path = Path(__file__).parent

    def build_models_1(self):
        reg_data_1 = pd.read_csv(
            self.base_path / "xfmr_catalog_dry_type_distribution_transformers.csv"
        )
        transformers = []

        for _, row in reg_data_1.iterrows():
            primary_voltage = row["primary voltage"]
            primary_voltage = max([float(v) for v in primary_voltage.split(" x ")])
            tap_info = row["tap arrangement"]
            tap_info = [x.split(" at ") for x in tap_info.split(", ")]
            tap_info = [[t for t in tt if " x " not in t] for tt in tap_info]
            total_taps = sum([int(tt[0]) for tt in tap_info])
            xfmr_taps = [int(t[0]) * float(t[1].replace("%", "")) for t in tap_info]
            taps = [1 + t / 100.0 for t in xfmr_taps]
            nphases = 3 if row["phases"] == "Three-Phase" else 1
            kva_rating = float(row["kva_rating"])

            clean = ["delta", "midtap", " ", "Y"]
            secondary_voltages = row["secondary voltage"]
            for c in clean:
                secondary_voltages = secondary_voltages.replace(c, "")
            secondary_voltages = [float(s) for s in secondary_voltages.split("/")]
            nt = max(secondary_voltages) / min(secondary_voltages)
            is_center_tapped = np.isclose(nt, 2.0)

            conn = (
                ConnectionType.STAR
                if "Y/" in row["secondary voltage"]
                else ConnectionType.DELTA
            )

            winding_1 = WindingEquipment(
                resistance=row["pct r"] / 2,
                is_grounded=False,
                rated_voltage=PositiveVoltage(primary_voltage, "volt"),
                rated_power=PositiveApparentPower(kva_rating, "kilova"),
                connection_type=ConnectionType.STAR,
                num_phases=nphases,
                tap_positions=[1.0] * nphases,
                total_taps=total_taps,
                voltage_type=VoltageTypes.LINE_TO_LINE,
                min_tap_pu=min(taps),
                max_tap_pu=max(taps),
            )

            winding_2 = WindingEquipment(
                resistance=row["pct r"] / 2,
                is_grounded=False,
                rated_voltage=PositiveVoltage(primary_voltage, "volt"),
                rated_power=PositiveApparentPower(kva_rating, "kilova"),
                connection_type=conn,
                num_phases=nphases,
                tap_positions=[1.0] * nphases,
                total_taps=total_taps,
                voltage_type=VoltageTypes.LINE_TO_GROUND,
                min_tap_pu=min(taps),
                max_tap_pu=max(taps),
            )

            xfmr = DistributionTransformerEquipment(
                name=row["catalog id"],
                pct_no_load_loss=row["no load loss - watts"]
                / (kva_rating * 1000)
                * 100.0,
                pct_full_load_loss=row["total loss - watts"]
                / (kva_rating * 1000)
                * 100.0,
                is_center_tapped=is_center_tapped,
                windings=[winding_1, winding_2],
                coupling_sequences=[SequencePair(0, 1)],
                winding_reactances=[float(row["pct x"])],
            )

            transformers.append(xfmr)

        return transformers


def build_dry_type_xfmr():
    a = Model()
    return a.build_models_1()
