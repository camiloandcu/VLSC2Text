#!/usr/bin/env bash
#SBATCH --job-name=lsc5-opaque-tcn
#SBATCH --partition=estudiantes
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:15:00

set -euo pipefail
umask 077
source "$HOME/venv_entrenamiento/bin/activate"
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export PYTHONPATH="$SLURM_SUBMIT_DIR/src"
python -m lsc5.cli fit-temporal "$@"
