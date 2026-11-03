import os
import tempfile

# Before any app import: keep tests away from the real data directory.
os.environ["SHELF_DATA_DIR"] = tempfile.mkdtemp(prefix="shelf-help-test-")
