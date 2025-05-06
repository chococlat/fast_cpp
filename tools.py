import argparse
import subprocess
import os
import sys
import shutil
import json
import re
import platform

BUILD_DIR = "build"
IS_WINDOWS = platform.system() == "Windows"

def get_config():
    with open(".project.config.json","r") as pc:
        return json.loads(pc.read())

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


def cmake_gen():
    config = get_config()
    if not config.get("CLANG_FLAGS"):
        config["CLANG_FLAGS"] = ""
        
    os.makedirs(BUILD_DIR, exist_ok=True)
    cmake_command = [
        "cmake",
        "-G", "Ninja",  # Strongly recommended to avoid MSVC detection on Windows
        "-DCMAKE_C_COMPILER=clang",          # Recommended: also set C compiler
        "-DCMAKE_CXX_COMPILER=clang++",
        f"-DCMAKE_CXX_FLAGS={config['CLANG_FLAGS']}",
        ".."
    ]
    print("CMAKE COMMAND : "," ".join(cmake_command))
    
    subprocess.run(cmake_command, cwd=BUILD_DIR, check=True)
    subprocess.run(["cmake", "--build", "."], cwd=BUILD_DIR, check=True)


def build(target):
    command = ["cmake", "--build", "."]
    if target:
        if target not in get_apps():
            print(f"App called {target} doesn't exist.")
            sys.exit(1)
        command.extend(["--target", target])
    subprocess.run(command, cwd=BUILD_DIR, check=True)


def run(app):
    if app == "core":
        print("CORE is not intended to be run individually.")
        sys.exit(1)
    if app not in get_apps():
        print(f"App called {app} doesn't exist.")
        sys.exit(1)
    exe_path = f"{BUILD_DIR}/apps/{app}/{app}"
    if IS_WINDOWS:
        exe_path+=".exe"
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
    

def add_external_dependency():
    alias = input("Dependency name (CMake target of the library) : ")
    repo = input("Git repository : ")
    tag = input("Git repository tag (version) : ")
    config = get_config()
    if not isinstance(config.get("EXTERNAL_DEPENDENCIES"),list):
        config["EXTERNAL_DEPENDENCIES"] = []
    for dep in config["EXTERNAL_DEPENDENCIES"]:
        if dep["ALIAS"] == alias:
            response = input(f"Dependency with alias {alias} already exists. Do you want to update it? (y/N)")
            if response in ("y","Y"):
                dep = {
                    "ALIAS":alias,
                    "GIT_REPOSITORY":repo,
                    "GIT_TAG":tag
                }
                set_config(config)
                print("Dependency update in .project.config.json")
                sys.exit(0)
            else:
                print("Exiting ... ")
                sys.exit(1)
    config["EXTERNAL_DEPENDENCIES"].append({
        "ALIAS":alias,
        "GIT_REPOSITORY":repo,
        "GIT_TAG":tag
    })
    set_config(config)
    print("Dependency added in .project.config.json")


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
        if isinstance(config.get("EXTERNAL_DEPENDENCIES"),list):
            s = ""
            for dep in config["EXTERNAL_DEPENDENCIES"]:
                s +=f"""
FetchContent_Declare(
    {dep["ALIAS"]}
    GIT_REPOSITORY {dep["GIT_REPOSITORY"]}
    GIT_TAG        {dep["GIT_TAG"]}
)
FetchContent_MakeAvailable({dep["ALIAS"]})
"""
            rendered = rendered.replace("{{EXTERNAL_DEPENDENCIES}}",s)
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
        if isinstance(config.get("EXTERNAL_DEPENDENCIES"),list):
            s = ""
            for dep in config["EXTERNAL_DEPENDENCIES"]:
                s += f"target_link_libraries(core PUBLIC {dep['ALIAS']}::{dep['ALIAS']})\n"
            rendered = rendered.replace("{{LIBRARIES}}",s)
                
        
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


def clean():
    print(f"Removing build directory: {BUILD_DIR}")
    try:
        shutil.rmtree(BUILD_DIR)
        print("Clean complete.")
    except FileNotFoundError:
        print(f"No such directory: {BUILD_DIR}")


def format_code():
    print("Formatting code...")
    subprocess.run(["clang-format", "-i", "*.cpp", "*.h"])


def main():
    parser = argparse.ArgumentParser(description="Project management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # CreateProject command
    subparsers.add_parser("create_project")
    
    # CreateApp command
    subparsers.add_parser("create_app")
    
    # AddExternalDependency command
    subparsers.add_parser("add_external_dependency")
    
    # Render command
    subparsers.add_parser("render")

    # Build command
    subparsers.add_parser("cmake_gen")
    
    # SmartBuild command
    parser_build = subparsers.add_parser("build")
    parser_build.add_argument("target", nargs="?", default=None, help="Build target name (default: all)")

    # Run command
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("app", help="Run app name")

    # Test command
    subparsers.add_parser("test")

    # Clean command
    subparsers.add_parser("clean")

    # Format command
    subparsers.add_parser("format")

    args = parser.parse_args()

    if args.command == "cmake_gen":
        cmake_gen()
    elif args.command == "build":
        build(args.target)
    elif args.command == "render":
        render_cmake_files()
    elif args.command == "add_external_dependency":
        add_external_dependency()
    elif args.command == "create_project":
        create_project()
    elif args.command == "create_app":
        create_app()
    elif args.command == "run":
        run(args.app)
    elif args.command == "test":
        test()
    elif args.command == "clean":
        clean(args.build_dir)
    elif args.command == "format":
        format_code()


if __name__ == "__main__":
    main()
