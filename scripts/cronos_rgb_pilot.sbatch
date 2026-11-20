#!/usr/bin/env bash
#SBATCH --job-name=lsc5-rgb-head-pilot
#SBATCH --partition=estudiantes
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:05:00

set -euo pipefail
umask 077
source "$HOME/venv_entrenamiento/bin/activate"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
export PYTHONPATH="$SLURM_SUBMIT_DIR/src"
python -m lsc5.cli fit-rgb-head "$@" --pilot
while [[ $# -gt 0 ]]; do
    case "$1" in
        --manifest) manifest="$2"; shift 2;;
        --cache) cache="$2"; shift 2;;
        --out) run="$2"; shift 2;;
        *) shift;;
    esac
done
python -m lsc5.cli restore-rgb-cache --manifest "$manifest" --cache "$cache" --run "$run" --out "$run/cache_restoration.json"
