# APEX

Fork of [APEX](https://gitlab.com/machine-biology-group-public/apex) (hosted on GitLab),
adapted for integration with the
[battleamp-snakemake](https://github.com/szczurek-lab/battleamp-snakemake) benchmarking
pipeline.

## Supported tasks

AMP classification (via MIC thresholding) and AMP regression (MIC prediction).

## Reference

Wan, F., Torres, M.D.T., Peng, J. et al. Deep-learning-enabled antibiotic discovery through molecular de-extinction. Nat. Biomed. Eng 8, 854–871 (2024). https://doi.org/10.1038/s41551-024-01201-x

## Model overview

APEX is a 40-model ensemble (8 hyperparameter configurations, each trained 5 times) of
bidirectional GRU networks with attention. It predicts MIC values simultaneously across
34 bacterial strains. Because APEX natively outputs multi-strain predictions, the
pipeline derives six benchmark variants by post-processing a single inference pass:

| Variant | Description |
|---|---|
| `apex-min` | Minimum MIC across all 34 strains |
| `apex-ecoli` | Mean MIC across 3 E. coli strains |
| `apex-saureus` | Mean MIC across 2 S. aureus strains |
| `apex-kpneumoniae` | Single strain (ATCC13883) |
| `apex-abaumannii` | Single strain (ATCC19606) |
| `apex-paeruginosa` | Mean of 2 P. aeruginosa strains |

All variants share the same length constraint of 50 amino acids. APEX predicts MIC in
micromolar units; for comparison with ground truth labels, values are converted to the
benchmark target unit using per-peptide molecular weights computed from residue masses.

## Training data

`training_data/APEXDB.csv` is the dataset APEX was trained on, fetched unmodified from
`app/frontend/public/APEXDB.csv` of the upstream repository at commit
`203055125196eee0b0f3c456335d3e9aede0e942`, on 2026-09-02.

1,736 peptides, 2 to 50 residues, standard 20 amino acids only, with MIC values against 11
strains. The `Group (APEX training)` column carries the authors' own split:

| Group | Peptides | Role |
|---|---|---|
| `CV` | 1,388 | cross-validation |
| `Ind` | 348 | independent test |

The strain columns cover every benchmarked variant: A. baumannii ATCC 19606, three E. coli
strains, K. pneumoniae ATCC 13883, two P. aeruginosa strains and two S. aureus strains.

The same directory in the upstream repository also holds `db.csv`, which contains placeholder
sequences rather than data, and is not kept.

## Requirements

- Python 3.10
- conda (for environment creation by the pipeline)
- NVIDIA GPU
- 40 pretrained weight files in `trained_models/`
- 
`torch.load` calls were updated for compatibility with PyTorch 2.6+. Only wrapper
scripts and output formatting were modified; the model architecture and weights are
unchanged.

## Installation

```bash
conda create -n apex python=3.10
conda activate apex
sh setup.sh
```

Test whether everything works:

```bash
sh inference.sh sample.fasta results.tsv min
```

## Usage within the pipeline

This repository is included as a git submodule in battleamp-snakemake:

```bash
cd battleamp-snakemake
git submodule add git@github.com:szczurek-lab/BattleAMP-apex.git models/apex
```

The pipeline runs inference once and automatically splits the output into
variant-specific prediction files.

## Notes

- Maximum sequence length is 50 amino acids. Longer sequences are skipped by the
  pipeline's prefilter step.
- Only the 20 standard amino acids are supported (the model pads to 52 tokens with
  start/end tokens).
- The multi-output inference pattern avoids running the 40-model ensemble six separate
  times.

## License

Penn Software APEX, Copyright (C) 2022 The Trustees of the University of
Pennsylvania. Use is limited to non-profit research purposes. The full notice is in
`LICENSE`, reproduced from the upstream repository as its terms require.