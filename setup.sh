#!/usr/bin/env bash
set -euo pipefail

# Dependencies come from environment.yaml. The original requirements.txt pins
# torch==1.13.0 and nvidia-*-cu11 wheels, which would override the solver's
# driver-matched build; it is deliberately not used.

# Verify model weights exist (8 architectures x 5 repeats = 40 models)
expected_count=40
actual_count=$(ls trained_models/trained_all_model_* 2>/dev/null | wc -l)
if [ "$actual_count" -ne "$expected_count" ]; then
    echo "ERROR: Expected $expected_count model weight files in trained_models/, found $actual_count" >&2
    exit 1
fi
echo "APEX setup complete: $actual_count ensemble model weights verified"