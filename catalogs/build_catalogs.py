from gdm import DistributionSystem
from pathlib import Path
import os


from capacitors.catalog_builder import build_capacitor_models
from conductors.catalog_builder import build_conductor_models
from pv_and_inveter.catalog_builder import build_pv_and_inverter_models
from transformers.catalog_builder import build_transformer_models
from regulators.catalog_builder import build_regulator_models

capacitors = build_capacitor_models()
conductors_and_cables = build_conductor_models()
pvs_and_inveters = build_pv_and_inverter_models()
transformers = build_transformer_models()
xfmr_system = DistributionSystem(auto_add_composed_components=True)
xfmr_system.add_components(*transformers)
regulators = build_regulator_models(xfmr_system)

master_catalog = DistributionSystem(auto_add_composed_components=True)
master_catalog.add_components(*capacitors)
master_catalog.add_components(*conductors_and_cables)
master_catalog.add_components(*pvs_and_inveters)
master_catalog.add_components(*transformers)
master_catalog.add_components(*regulators)


master_catalog.info()