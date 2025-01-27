input_path="$1"
output_path="$2"
mode="$3" # ecoli, saureus

python predict.py "$input_path" "$output_path" "$mode"