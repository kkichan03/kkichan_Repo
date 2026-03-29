from pathlib import Path
import json, random

LOG_FILE = Path.home() / "shred_log.json"

def shred_file(filepath: str) -> bool:
    p = Path(filepath)
    size = p.stat().st_size
    for pat in [b'\x00', b'\xFF', None]:
        p.write_bytes(pat * size if pat else bytes(random.getrandbits(8) for _ in range(size)))
    p.unlink()
    records = json.loads(LOG_FILE.read_text("utf-8")) if LOG_FILE.exists() else []
    records.append({"파일명": p.name, "결과": "성공"})
    LOG_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), "utf-8")
    return True
