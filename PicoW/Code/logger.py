import time

LOG_FILE = "log.csv"
LOG_INTERVAL = 10  # seconds
_last_log = 0

def log_data(data):
    global _last_log
    now = time.time()

    if now - _last_log < LOG_INTERVAL:
        return

    _last_log = now

    try:
        with open(LOG_FILE, "a") as f:
            line = "{},{},{},{},{},{},{}\n".format(
                now,
                data["s1"],
                data["s2"],
                data["s3"],
                data["i0"],
                data["i1"],
                data["o0"],
                data["o1"]
            )
            f.write(line)
    except:
        pass
