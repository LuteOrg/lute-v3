import os
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

CONFIG_PATH = Path("lute/config/config.yml")
DATA_DIR = Path("data")
TEMPLATE_DIR = Path("lute/templates")


def check_config():
    if not CONFIG_PATH.exists():
        print(f"[FAIL] Config file not found: {CONFIG_PATH}")
        # Not strictly failure if running in some weird mode, but usually required.
        return False
    try:
        with open(CONFIG_PATH, "r") as f:
            yaml.safe_load(f)
        print(f"[OK] Config file readable: {CONFIG_PATH}")
    except PermissionError:
        print(f"[FAIL] PermissionError reading {CONFIG_PATH}. Check Full Disk Access!")
        return False
    except Exception as e:
        print(f"[FAIL] Error reading config: {e}")
        return False
    return True


def check_db_permissions():
    # If using dev settings, data dir is likely 'data'.
    # We can try creating a dummy file.
    test_file = DATA_DIR / ".test_write_perm"
    try:
        if not DATA_DIR.exists():
            # Try creating it
            DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(test_file, "w") as f:
            f.write("check")
        os.remove(test_file)
        print(f"[OK] Data directory writable: {DATA_DIR}")
    except PermissionError:
        print(f"[FAIL] PermissionError writing to {DATA_DIR}. Check Full Disk Access!")
        return False
    except Exception as e:
        print(f"[FAIL] Error writing to data dir: {e}")
        return False
    return True


def check_jinja_templates():
    if not TEMPLATE_DIR.exists():
        print(f"[WARN] Template directory not found: {TEMPLATE_DIR}")
        return True  # Can't check if missing

    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        # Test _form.html specifically as it was problematic
        target = "term/_form.html"
        env.get_template(target)
        print(f"[OK] Jinja template syntax valid: {target}")
    except Exception as e:
        print(f"[FAIL] Jinja syntax error in {target}: {e}")
        return False
    return True


if __name__ == "__main__":
    print("Verifying Lute Environment...")
    checks = [check_config(), check_db_permissions(), check_jinja_templates()]
    if all(checks):
        print("\n[SUCCESS] Environment looks good!")
        sys.exit(0)
    else:
        print("\n[FAIL] Environment issues detected.")
        sys.exit(1)
