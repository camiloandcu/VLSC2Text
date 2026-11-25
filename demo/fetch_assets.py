"""Download the private demo assets (weights, guide videos, references) at container start.

Needs HF_TOKEN (read access) and LSC5_ASSETS_REPO; writes into LSC5_ASSETS.
"""
import os
from huggingface_hub import snapshot_download

snapshot_download(repo_id=os.environ["LSC5_ASSETS_REPO"], repo_type="dataset", local_dir=os.environ["LSC5_ASSETS"],
                  token=os.environ["HF_TOKEN"])
print("assets ready")
