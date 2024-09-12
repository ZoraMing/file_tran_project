from pathlib import Path

import settings


BASE_DIR = Path(__file__).resolve().parent.parent

print(BASE_DIR)
print(settings.MEDIA_ROOT)
