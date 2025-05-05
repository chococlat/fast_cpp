import argparse
import subprocess
import os
import sys
import shutil
import json
import re


def get_config():
    with open(".project.config.json","r") as pc:
        return json.loads(pc.read())

def set_config(config):
    with open(".project.config.json","w") as pc:
        pc.write(json.dumps(config,indent=2))
        
def is_valid_folder_name(name):
    # Must be non-empty
    if not name:
        return False

    # Only allow alphanumerics, underscores, and dashes
    # No spaces or other special characters
    pattern = r'^[A-Za-z0-9_-]+$'

    return bool(re.fullmatch(pattern, name))

def build(build_dir="build"):
    os.makedirs(build_dir, exist_ok=True)
    subprocess.run(["cmake", ".."], cwd=build_dir, check=True)
    subprocess.run(["cmake", "--build", "."], cwd=build_dir, check=True)

def run(build_dir="build", exe=get_config()["PROJECT_NAME"]):
    exe_path = os.path.join(build_dir, exe)
    if not os.path.exists(exe_path):
        print(f"Executable not found: {exe_path}")
        sys.exit(1)
    subprocess.run([exe_path], check=True)


def find_cpp_files(dir_name):
    cpp_files = []
    for root, _, files in os.walk(dir_name):
        for file in files:
            if file.endswith(".cpp"):
                full_path = os.path.join(root, file).replace("\\","/")
                cpp_files.append("/".join(full_path.split("/")[len(dir_name.split("/")):]))
    print(f"SRC files found under {dir_name} : \n    {"\n    ".join(cpp_files)}")
    return cpp_files

def create_project():
    name = input("New project name : ")
    config = get_config()
    config["PROJECT_NAME"] = name
    set_config(config)
    

def create_app():
    name = input("New app name : ")
    if os.path.exists(f"apps/{name}"):
        print(f"App named {name} already exists")
        sys.exit(1)
    if not is_valid_folder_name(name):
        print(f"The provided name contains unallowed characters. Use only A-Z,a-z,0-9,-,_")
        sys.exit(1)
    config = get_config()
    if isinstance(config.get("APPS"),list) and name in config.get("APPS"):
        print(f"Broken config: The app exists in config but not in the apps directory.")
        sys.exit(1)
    if not isinstance(config.get("APPS"),list):
        config["APPS"] = []
    config["APPS"].append(name)
    set_config(config)
    
    os.makedirs(f"apps/{name}/src/subdir")
    os.makedirs(f"apps/{name}/include/subdir")
    shutil.copyfile(".defaults/main.cpp.default",f"apps/{name}/main.cpp")
    shutil.copyfile(".defaults/class.cpp.default",f"apps/{name}/src/subdir/class.cpp")
    shutil.copyfile(".defaults/class.hpp.default",f"apps/{name}/include/subdir/class.hpp")


def render_cmake_files():
    config = get_config()
    main_file = ".templates/CMakeLists.main.template"
    app_file = ".templates/CMakeLists.app.template"
    core_file = ".templates/CMakeLists.core.template"
    if not os.path.exists(main_file) or not os.path.exists(app_file) or not os.path.exists(core_file):
        print(f"File not found: {main_file} or {app_file} or {core_file} missing")
        sys.exit(1)
    
    with open(main_file,"r") as mr:
        rendered = mr.read().replace("{{PROJ_NAME}}",config["PROJECT_NAME"])
        if isinstance(config.get("APPS"),list):
            s = ""
            for appname in config["APPS"]:
                s += f"add_subdirectory(apps/{appname})\n"
            rendered = rendered.replace("{{APP_INCLUSIONS}}", s)
                
        
    with open("CMakeLists.txt","w") as mw:
        mw.write(rendered)
        
    corefiles = find_cpp_files("core")
    s = ""
    for f in corefiles:
        s += f"    \"{f}\"\n"
    with open(core_file, "r") as cr:
        rendered = cr.read().replace("{{SRC_FILES}}",s)
    with open("core/CMakeLists.txt","w") as cw:
        cw.write(rendered)
    
    if isinstance(config.get("APPS"),list):
        for appname in config["APPS"]:
            files = find_cpp_files(f"apps/{appname}")
            s = ""
            for f in files:
                s += f"    \"{f}\"\n"
            with open(app_file,"r") as ar:
                rendered = ar.read().replace("{{SRC_FILES}}",s)
                rendered = rendered.replace("{{APP_NAME}}", appname)
            with open(f"apps/{appname}/CMakeLists.txt","w") as aw:
                aw.write(rendered)
    

def test():
    print("Running tests...")
    # Placeholder: Add your test runner here
    subprocess.run(["ctest", "--output-on-failure"], cwd="build", check=True)

def clean(build_dir="build"):
    print(f"Removing build directory: {build_dir}")
    try:
        shutil.rmtree(build_dir)
        print("Clean complete.")
    except FileNotFoundError:
        print(f"No such directory: {build_dir}")

def format_code():
    print("Formatting code...")
    subprocess.run(["clang-format", "-i", "*.cpp", "*.h"])

def main():
    parser = argparse.ArgumentParser(description="Project management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # CreateProject command
    parser_build = subparsers.add_parser("create_project")
    
    # CreateApp command
    parser_build = subparsers.add_parser("create_app")
    
    # Render command
    parser_build = subparsers.add_parser("render")

    # Build command
    parser_build = subparsers.add_parser("build")
    parser_build.add_argument("--build-dir", default="build")

    # Run command
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("--build-dir", default="build")
    parser_run.add_argument("--exe", default=get_config()["PROJECT_NAME"])

    # Test command
    subparsers.add_parser("test")

    # Clean command
    parser_clean = subparsers.add_parser("clean")
    parser_clean.add_argument("--build-dir", default="build")

    # Format command
    subparsers.add_parser("format")

    args = parser.parse_args()

    if args.command == "build":
        build(args.build_dir)
    elif args.command == "render":
        render_cmake_files()
    elif args.command == "create_project":
        create_project()
    elif args.command == "create_app":
        create_app()
    elif args.command == "run":
        run(args.build_dir, args.exe)
    elif args.command == "test":
        test()
    elif args.command == "clean":
        clean(args.build_dir)
    elif args.command == "format":
        format_code()

if __name__ == "__main__":
    main()
