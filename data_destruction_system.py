import json, random, hashlib, datetime
from pathlib import Path

LOG_DIR   = Path.home() / ".overturn" / "shred_log"
SUPPORTED = {".txt", ".pdf", ".hwp", ".hwpx", ".docx", ".doc", ".xlsx", ".csv"}


def shred_file(filepath: str) -> bool:
    p = Path(filepath)

    if not p.exists():
        _log(filepath, False, "파일 없음")
        return False

    if p.suffix.lower() not in SUPPORTED:
        _log(filepath, False, f"지원하지 않는 형식: {p.suffix}")
        return False

    size = p.stat().st_size
    sha  = hashlib.sha256(p.read_bytes()).hexdigest()

    try:
        for pattern in [b'\x00', b'\xFF', None]:
            p.write_bytes(pattern * size if pattern else bytes(random.getrandbits(8) for _ in range(size)))
        p.unlink()
    except Exception as e:
        _log(filepath, False, str(e), size, sha)
        return False

    _log(filepath, True, "", size, sha)
    return True


def shred_with_callback(filepaths: list[str], put: callable) -> int:
    count = 0
    for fp in filepaths:
        if shred_file(fp):
            count += 1
            put(("log", f"[파기] {Path(fp).name} 성공"))
            put(("log", f"[파기] {count}건이 성공적으로 파기되었습니다."))
        else:
            put(("log", f"[파기] {Path(fp).name} 실패"))
    return count


def _log(filepath, success, reason="", size=0, sha=""):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"shred_{datetime.date.today()}.json"
    records  = json.loads(log_file.read_text("utf-8")) if log_file.exists() else []
    records.append({
        "파일명": Path(filepath).name,
        "결과":   "성공" if success else f"실패: {reason}",
    })
    log_file.write_text(json.dumps(records, ensure_ascii=False, indent=2), "utf-8")
