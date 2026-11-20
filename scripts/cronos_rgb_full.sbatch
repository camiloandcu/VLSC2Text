#!/usr/bin/env bash
#SBATCH --job-name=lsc5-rgb-head
#SBATCH --partition=estudiantes
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:15:00

set -euo pipefail
umask 077
source "$HOME/venv_entrenamiento/bin/activate"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
export PYTHONPATH="$SLURM_SUBMIT_DIR/src"
python -m lsc5.cli fit-rgb-head "$@"
