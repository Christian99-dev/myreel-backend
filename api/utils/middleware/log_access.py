import logging

def log_access(path: str, status_code: int, duration: float, access_time: str, additional: str = ""):
    logging.getLogger("endpoints").info((
        f"Access time: {access_time}, "
        f"Status: {status_code}, "
        f"Duration: {duration:.4f} seconds"
        f"Path: {path}, "
        f"{additional}"
    ))