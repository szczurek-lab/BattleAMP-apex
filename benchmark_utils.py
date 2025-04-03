import pandas as pd
from typing import Dict, List


def read_fasta(file_path):
    fasta_data = {}
    with open(file_path, "r") as file:
        seq_id, sequence = None, []
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                if seq_id:
                    fasta_data[seq_id] = "".join(sequence)
                seq_id, sequence = line[1:], []
            else:
                sequence.append(line)
        if seq_id:
            fasta_data[seq_id] = "".join(sequence)
    return fasta_data

def extract_minimal_predictions(df: pd.DataFrame, id_mapping: Dict) -> pd.DataFrame:
    min_strain = df.idxmin(axis=1).values.tolist()
    df = df.min(axis=1).reset_index()

    df.columns = ['Sequence', 'MIC']
    df['Strain'] = min_strain
    df['Sequence_id'] = df['Sequence'].map(id_mapping)
    df['MIC_unit'] = 'uM'

    return df

def extract_species_predictions(df: pd.DataFrame, id_mapping: Dict,
                                selected_cols: List[str]) -> pd.DataFrame:
    df = df[selected_cols].mean(axis=1).reset_index()

    df.columns = ['Sequence', 'MIC']
    df['Sequence_id'] = df['Sequence'].map(id_mapping)
    df['MIC_unit'] = 'uM'

    return df
