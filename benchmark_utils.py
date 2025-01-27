


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