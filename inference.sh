#!/usr/bin/env bash
set -euo pipefail

input_path="$1"
output_path="$2"

# Run APEX ensemble in multioutput mode.
# Loads all 40 models once and predicts MIC for 34 bacterial strains,
# then writes species-level aggregations as separate files.
python predict.py "$input_path" "$output_path" multioutput

# predict.py multioutput writes:
#   $output_path                      (raw 34-strain MIC matrix)
#   ${output_base}-min.tsv            (min MIC across all strains)
#   ${output_base}-ecoli.tsv          (mean E. coli MIC)
#   ${output_base}-saureus.tsv        (mean S. aureus MIC)
#   ${output_base}-kpneumoniae.tsv
#   ${output_base}-abaumannii.tsv
#   ${output_base}-paeruginosa.tsv
#
# All variant files have a pandas index column and uppercase 'Sequence'.
# Convert each to pipeline-standard regressor format.

output_base="${output_path%.tsv}"

for mode in min ecoli saureus kpneumoniae abaumannii paeruginosa; do
    variant_file="${output_base}-${mode}.tsv"
    if [ -f "$variant_file" ]; then
        python3 -c "
import pandas as pd
df = pd.read_csv('${variant_file}', sep='\t', index_col=0)
df = df.rename(columns={'Sequence': 'sequence'})
df[['sequence', 'MIC', 'MIC_unit']].to_csv('${variant_file}', sep='\t', index=False)
"
    fi
done
