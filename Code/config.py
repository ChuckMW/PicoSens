import json
from debug import log

ACTIVE_CONFIG_FILE = "config.json"
DEFAULT_CONFIG_FILE = "def_config.json"


def load_json(path):
    """Load a JSON file safely."""
    try:
        with open(path) as f:
            data = json.load(f)
            log(f"Loaded JSON file: {path}")
            return data
    except Exception as e:
        log(f"Failed to load {path}: {e}")
        return None


def load_config():
    """Load active config.json, or fall back to def_config.json."""
    log("Loading active config.json...")

    cfg = load_json(ACTIVE_CONFIG_FILE)
    if cfg is not None:
        return cfg

    log("Active config missing or invalid — loading defaults...")

    defaults = load_json(DEFAULT_CONFIG_FILE)
    if defaults is None:
        log("ERROR: def_config.json missing or invalid!")
        raise Exception("No valid configuration available")

    # Write defaults to active config
    save_config(defaults)
    return defaults


def save_config(cfg):
    """Save configuration to config.json."""
    log("Saving config.json...")
    try:
        with open(ACTIVE_CONFIG_FILE, "w") as f:
            json.dump(cfg, f)
        log("Config saved")
    except Exception as e:
        log(f"Failed to save config.json: {e}")

