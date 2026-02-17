#!/usr/bin/env bash
set -euo pipefail

# Install only the dependencies APEX needs for inference.
# The original requirements.txt pins torch==1.13.0 (Python <3.12 only)
# and nvidia-* packages that are not needed on CPU.  We install a
# compatible torch instead of using the original requirements.txt.
pip install \
    numpy==1.26.4 \
    pandas==2.2.1 \
    scikit-learn==1.4.1.post1 \
    scipy==1.12.0 \
    "torch>=2.2,<3"

# Verify model weights exist (8 architectures x 5 repeats = 40 models)
expected_count=40
actual_count=$(ls trained_models/trained_all_model_* 2>/dev/null | wc -l)
if [ "$actual_count" -ne "$expected_count" ]; then
    echo "ERROR: Expected $expected_count model weight files in trained_models/, found $actual_count" >&2
    exit 1
fi
echo "APEX setup complete: $actual_count ensemble model weights verified"