from catalogs.transformers.three_phase_distribution_xfmr_split_phase import build_split_phase_xfmr
from catalogs.transformers.three_phase_distribution_xfmr import build_three_phase_xfmr
from catalogs.transformers.catalog import build_dry_type_xfmr

def build_transformer_models():
    transformers = []
    transformers.extend(build_three_phase_xfmr())
    transformers.extend(build_split_phase_xfmr())
    transformers.extend(build_dry_type_xfmr())
    return transformers