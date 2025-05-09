import json, re, os

def get_config():
    try:
        with open(".project.config.json","r") as pc:
            return json.loads(pc.read())
    except Exception:
        return {}

def set_config(config):
    with open(".project.config.json","w") as pc:
        pc.write(json.dumps(config,indent=2))

def get_apps():
    apps = get_config().get("APPS")
    if not apps:
        return []
    return apps
    
       
def is_valid_folder_name(name):
    # Must be non-empty
    if not name:
        return False

    # Only allow alphanumerics, underscores, and dashes
    # No spaces or other special characters
    pattern = r'^[A-Za-z0-9_-]+$'

    return bool(re.fullmatch(pattern, name))

def find_cpp_files(dir_name):
    cpp_files = []
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith(".cpp"):
                full_path = os.path.join(root, file).replace("\\","/")
                cpp_files.append("/".join(full_path.split("/")[len(dir_name.split("/")):]))
    print(f"SRC files found under {dir_name} : \n    {"\n    ".join(cpp_files)}")
    return cpp_files