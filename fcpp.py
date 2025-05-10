import argparse
import subprocess
import os
import sys
import shutil
import json
import config as conf
from utils import get_config, set_config, get_apps, is_valid_folder_name, find_cpp_files


def cmake_gen():
    config = get_config()
    if not config.get("CLANG_FLAGS"):
        config["CLANG_FLAGS"] = ""
        
    os.makedirs(conf.BUILD_DIR, exist_ok=True)
    cmake_command = [
        "cmake",
        "-G", "Ninja",  # Strongly recommended to avoid MSVC detection on Windows
        "-DCMAKE_VERBOSE_MAKEFILE=ON",
        "-DCMAKE_BUILD_TYPE=Debug",
        "-DCMAKE_C_COMPILER=clang",          # Recommended: also set C compiler
        "-DCMAKE_CXX_COMPILER=clang++",
        f"-DCMAKE_CXX_CLANG_TIDY={os.path.abspath('build/clangtidy.sh')}",
        f"-DCMAKE_CXX_FLAGS={config['CLANG_FLAGS']}",
        ".."
    ]
    print("CMAKE COMMAND : "," ".join(cmake_command))
    
    
    subprocess.run(cmake_command, cwd=conf.BUILD_DIR, check=True)
    subprocess.run(["cmake", "--build", "."], cwd=conf.BUILD_DIR, check=True)
    
def render_debug_config_vscode():
    config = get_config()
    if isinstance(config.get("APPS"),list):
        launchjson = {
            "version": "0.2.0",
            "configurations": []
        }

        for appname in config["APPS"]:
            launchjson['configurations'].append({
                    "name": "(gdb) Launch "+ appname,
                    "type": "cppdbg",
                    "request": "launch",
                    "program": "${workspaceFolder}/build/apps/" + f"{appname}/{appname}",
                    "args": [],
                    "stopAtEntry": False,
                    "cwd": "${workspaceFolder}/apps/" + appname,
                    "environment": [],
                    "externalConsole": False,
                    "MIMode": "gdb",
                    "setupCommands": [
                        {
                            "description": "Enable pretty-printing for gdb",
                            "text": "-enable-pretty-printing",
                            "ignoreFailures": True
                        },
                        {
                            "description": "Set Disassembly Flavor to Intel",
                            "text": "-gdb-set disassembly-flavor intel",
                            "ignoreFailures": True
                        }
                    ]
                })
        os.makedirs(".vscode", exist_ok=True)
        with open(".vscode/launch.json","w") as lj:
            lj.write(json.dumps(launchjson, indent=2))


def build(target,force):
    if force:
        subprocess.run(["ninja", "-t", "clean"], cwd=conf.BUILD_DIR, check=True)
    command = ["cmake", "--build", "."]
    if target:
        if target not in get_apps():
            print(f"App called {target} doesn't exist.")
            return
        command.extend(["--target", target])
    subprocess.run(command, cwd=conf.BUILD_DIR, check=True)


def run(app):
    if app == "core":
        print("CORE is not intended to be run individually.")
        return
    if app not in get_apps():
        print(f"App called {app} doesn't exist.")
        return
    exe_path = f"{conf.BUILD_DIR}/apps/{app}/{app}"
    if conf.IS_WINDOWS:
        exe_path+=".exe"
    if not os.path.exists(exe_path):
        print(f"Executable not found: {exe_path}")
        return
    subprocess.run([exe_path], check=True)


def create_project():
    name = input("New project name : ")
    config = get_config()
    config["PROJECT_NAME"] = name
    config["CLANG_FLAGS"] = "-Wall -Wextra -O2 -g"
    set_config(config)
    os.makedirs("core/src/core",exist_ok=True)
    os.makedirs("core/include/core",exist_ok=True)
    with open("CorePackages.cmake","w") as w:
        w.write(conf.CMAKE_CORE_EDITABLE)
    with open("core/src/core/class.cpp","w") as w:
        w.write(conf.DEFAULT_CORECLASSCPP)
    with open("core/include/core/class.hpp","w") as w:
        w.write(conf.DEFAULT_CORECLASSHPP)
    with open("core/include/core/class.hpp","w") as w:
        w.write(conf.DEFAULT_CORECLASSHPP)
    print(f"Project {name} has been created !")
    print(f" - project.config.json added")
    print(f" - core directory added")
    print(f" - CorePackages.cmake added")

def create_app():
    name = input("New app name : ")
    if os.path.exists(f"apps/{name}"):
        print(f"App named {name} already exists")
        return
    if not is_valid_folder_name(name):
        print(f"The provided name contains unallowed characters. Use only A-Z,a-z,0-9,-,_")
        return
    config = get_config()
    if isinstance(config.get("APPS"),list) and name in config.get("APPS"):
        print(f"Broken config: The app exists in config but not in the apps directory.")
        return
    if not isinstance(config.get("APPS"),list):
        config["APPS"] = []
    config["APPS"].append(name)
    set_config(config)
    
    os.makedirs(f"apps/{name}/src/subdir")
    os.makedirs(f"apps/{name}/include/subdir")
    with open(f"apps/{name}/main.cpp","w") as w:
        w.write(conf.DEFAULT_MAINCPP)
    with open(f"apps/{name}/src/subdir/class.cpp","w") as w:
        w.write(conf.DEFAULT_CLASSCPP)
    with open(f"apps/{name}/include/subdir/class.hpp","w") as w:
        w.write(conf.DEFAULT_CLASSHPP)
    print(f"App {name} has been added !")
    

def add_external_dependency():
    print("Deprecated. Exiting...")
    return
    alias = input("Dependency name (CMake target of the library) : ")
    repo = input("Git repository : ")
    tag = input("Git repository tag (version) : ")
    link = input("Add library link (e.g. \"fmt::fmt\"): ")
    cmake_target = input("Does the library have cmake target (Y/n)")
    cmake_target = False if cmake_target in ("n","N") else True
    
    
    config = get_config()
    if not isinstance(config.get("EXTERNAL_DEPENDENCIES"),list):
        config["EXTERNAL_DEPENDENCIES"] = []
    for dep in config["EXTERNAL_DEPENDENCIES"]:
        if dep["ALIAS"] == alias:
            response = input(f"Dependency with alias {alias} already exists. Do you want to update it? (y/N)")
            if response in ("y","Y"):
                dep = {
                    "ALIAS" : alias,
                    "GIT_REPOSITORY" : repo,
                    "GIT_TAG" : tag,
                    "LIBRARY_LINK" : link,
                    "HAS_CMAKE_TARGET" : cmake_target
                }
                set_config(config)
                print("Dependency update in .project.config.json")
                sys.exit(0)
            else:
                print("Exiting ... ")
                return
    config["EXTERNAL_DEPENDENCIES"].append({
                    "ALIAS" : alias,
                    "GIT_REPOSITORY" : repo,
                    "GIT_TAG" : tag,
                    "LIBRARY_LINK" : link,
                    "HAS_CMAKE_TARGET" : cmake_target
                })
    set_config(config)
    print("Dependency added in .project.config.json")


def render_cmake_files():
    config = get_config()
    
    mr = conf.CMAKELISTS_ROOT
    rendered = mr.replace("{{PROJ_NAME}}",config["PROJECT_NAME"])
    
    if isinstance(config.get("EXTERNAL_DEPENDENCIES"),list) and False:
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
        rendered = rendered.replace("{{EXTERNAL_DEPENDENCIES}}", s)
    else:
        rendered = rendered.replace("{{EXTERNAL_DEPENDENCIES}}", "")
    if isinstance(config.get("APPS"),list):
        s = ""
        for appname in config["APPS"]:
            s += f"add_subdirectory(apps/{appname})\n"
        rendered = rendered.replace("{{APP_INCLUSIONS}}", s)
    else:
        rendered = rendered.replace("{{APP_INCLUSIONS}}", "")
                
    
    with open("CMakeLists.txt","w") as mw:
        mw.write(rendered)
        
    corefiles = find_cpp_files("core")
    s = ""
    for f in corefiles:
        s += f"    \"{f}\"\n"
    cr = conf.CMAKELISTS_CORE
    rendered = cr.replace("{{SRC_FILES}}",s)
    if isinstance(config.get("EXTERNAL_DEPENDENCIES"),list) and False:
        s = ""
        for dep in config["EXTERNAL_DEPENDENCIES"]:
            if dep['HAS_CMAKE_TARGET']:
                s += f"target_link_libraries(core PUBLIC {dep['ALIAS']}::{dep['ALIAS']})\n"
            else:
                s += f"target_include_directories(core PUBLIC ${{{dep['ALIAS']}_SOURCE_DIR}}/include)\n"
                
        rendered = rendered.replace("{{LIBRARIES}}",s)
    else:
        with open("CorePackages.cmake","r") as cp:
            rendered = rendered.replace("{{LIBRARIES}}", cp.read())
                
 
    with open("core/CMakeLists.txt","w") as cw:
        cw.write(rendered)
    
    if isinstance(config.get("APPS"),list):
        for appname in config["APPS"]:
            files = find_cpp_files(f"apps/{appname}")
            s = ""
            for f in files:
                s += f"    \"{f}\"\n"
            ar = conf.CMAKELISTS_APP
            rendered = ar.replace("{{SRC_FILES}}",s)
            rendered = rendered.replace("{{APP_NAME}}", appname)
            with open(f"apps/{appname}/CMakeLists.txt","w") as aw:
                aw.write(rendered)
    

def test():
    print("Running tests...")
    # Placeholder: Add your test runner here
    subprocess.run(["ctest", "--output-on-failure"], cwd="build", check=True)


def clean():
    print(f"Removing build directory: {conf.BUILD_DIR}")
    try:
        shutil.rmtree(conf.BUILD_DIR)
        print("Clean complete.")
    except FileNotFoundError:
        print(f"No such directory: {conf.BUILD_DIR}")


def format_code():
    print("Formatting code...")
    subprocess.run(["clang-format", "-i", "*.cpp", "*.h"])
    
def clangtidyfile():
    os.makedirs(conf.BUILD_DIR,exist_ok=True)
    with open(f"{conf.BUILD_DIR}/clangtidy.sh","w") as ct:
        ct.write("""
#!/bin/bash
CHECKS='-checks=bugprone-*,performance-*,modernize-*'
# Find the source file in the arguments
exec clang-tidy $CHECKS "$@"

# If no .cpp file found, just skip
exit 0
                 """)
    os.system(f"chmod +x {conf.BUILD_DIR}/clangtidy.sh")

def reload():
    render_cmake_files()
    print("- CMake files have been rendered.")
    clangtidyfile()
    print("- Clangtidy file has been copied to build dir.")
    cmake_gen()
    print("- CMake build directory has been created.")
    render_debug_config_vscode()
    print("- Debug configuration for vscode has been added.")

def project_wizard():
    create_project()
    while True:
        res = input("Add a new app? (Y/n)")
        if res in ("Y","y",""):
            create_app()
            continue
        break
    while False:
        res = input("Add a new external dependency? (Y/n)")
        if res in ("Y","y",""):
            add_external_dependency()
            continue
        break
    reload()
    
def help():
    print("""
          fcpp create_app       ->    To add a new app
          fcpp build            ->    To build the entire project
          fcpp build <app>      ->    To build a specific app
          fcpp fbuild           ->    To force build the entire project
          fcpp fbuild <app>     ->    To force build a specific app
          fcpp run <app>        ->    To run a specific app
          fcpp reload           ->    To regenerate configuration files. To be done everytime there are changes like:
                                      - New external dependencies
                                      - New app
                                      - Adding or deleting src or include files
          
          To add external dependencies, edit "CorePackages.cmake" in the root directory,
          where you will find some examples which you can uncomment (fmt,json,boost).
          If you use find_package(...) you will first need to install the package (e.g. apt)
          
          You can also use this file to add custom configuration at core component level.
          
          
          """)

def main():
    parser = argparse.ArgumentParser(description="Project management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # CreateProject command
    subparsers.add_parser("create_project")
    
    subparsers.add_parser("reload")
    
    subparsers.add_parser("render_vscode_debug_json")
    
    # CreateApp command
    subparsers.add_parser("create_app")
    
    # AddExternalDependency command
    subparsers.add_parser("add_external_dependency")
    
    # Render command
    subparsers.add_parser("render")

    # Build command
    subparsers.add_parser("cmake_gen")
    
    # ForceBuild command
    parser_build = subparsers.add_parser("fbuild")
    parser_build.add_argument("target", nargs="?", default=None, help="Build target name (default: all)")
    
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
    elif args.command == "fbuild":
        build(args.target,force=True)
    elif args.command == "build":
        build(args.target,force=False)
    elif args.command == "reload":
        reload()
    elif args.command == "render_vscode_debug_json":
        render_debug_config_vscode()
    elif args.command == "render":
        render_cmake_files()
    elif args.command == "add_external_dependency":
        add_external_dependency()
    elif args.command == "create_project":
        project_wizard()
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
