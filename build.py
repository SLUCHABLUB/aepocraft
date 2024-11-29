#!/usr/bin/env python3

import argparse
import json
import os
import shutil as sh
import sys as system
import zipfile as zip

VERSION = "1.21.3"
DIRECTORIES = ["function", "recipe", "tags"]

DESCRIPTION = "A Minecraft datapack designed to make Minecraft more *realistic* without adding items and resources"


def copy_file(source, destination, zipfile):
    if zipfile is None:
        sh.copyfile(source, destination)
    else:
        with open(source, "rb") as source:
            with zipfile.open(destination, "w") as destination:
                destination.write(source.read())


def copy_directory(source, destination, zipfile):
    for root, _, files in os.walk(source):
        relative_root = os.path.relpath(root, start=source).strip("./")
        destination_root = os.path.join(destination, relative_root).rstrip("/")
        make_directory(destination_root, zipfile)

        for file in files:
            file_source = os.path.join(root, file)
            file_destination = os.path.join(destination_root, file)
            copy_file(file_source, file_destination, zipfile)


def write_file(path, content, zipfile):
    # required when writing to a zipfile
    content = bytes(content, "utf-8")
    opener = open if zipfile is None else zipfile.open
    with opener(path, "w") as file:
        file.write(content)


def make_directory(path, zipfile):
    if zipfile is None:
        os.makedirs(path)
    else:
        zipfile.mkdir(path)


def build():
    default_minecraft_directory = None

    match system.platform:
        case "linux":
            default_minecraft_directory = os.path.expanduser("~/.minecraft")
        case "darwin":
            default_minecraft_directory = os.path.expanduser("~/Library/Application Support/minecraft")
        case "win32":
            default_minecraft_directory = os.path.join(os.getenv("AppData"), ".minecraft")

    parser = argparse.ArgumentParser(description="Builds äpocraft")
    parser.add_argument("-o", "--output", help="The output zip-file or directory", default=f"aepocraft-{VERSION}")
    parser.add_argument("-m", "--minecraft", help="The minecraft instance folder (\".minecraft\")", default=default_minecraft_directory)
    args = parser.parse_args()

    if os.path.exists(args.output):
        print("output directory already exists")
        exit(1)
    if args.minecraft is None:
        print("no minecraft directory specified")
        exit(1)

    version_archive = os.path.join(args.minecraft, "versions", VERSION, VERSION + ".jar")
    pack_format: int
    with zip.ZipFile(version_archive, "r") as archive:
        with archive.open("version.json", "r") as file:
            version = json.loads(file.read())
            pack_format = version["pack_version"]["data"]
    
    root = args.output
    zipfile = None
    if args.output.endswith(".zip"):
        zipfile = zip.ZipFile(args.output, "w") 
        root = ""
    else:
        os.makedirs(root)

    data_directory = os.path.join(root, "data")
    make_directory(data_directory, zipfile)

    mcmeta_directory = os.path.join(root, "pack.mcmeta")
    write_file(mcmeta_directory, json.dumps({
        "pack": {
            "description": DESCRIPTION,
            "pack_format": pack_format
        }
    }), zipfile)

    aepocraft_directory = os.path.join(data_directory, "aepocraft")
    make_directory(aepocraft_directory, zipfile)

    for directory in DIRECTORIES:
        destination = os.path.join(aepocraft_directory, directory)
        copy_directory(directory, destination, zipfile)

    minecraft_directory = os.path.join(data_directory, "minecraft")
    
    copy_directory("override", minecraft_directory, zipfile)

    minecraft_tags_directory = os.path.join(minecraft_directory, "tags")
    make_directory(minecraft_tags_directory, zipfile)

    function_tags_directory = os.path.join(minecraft_tags_directory, "function")
    make_directory(function_tags_directory, zipfile)

    for name in ["load", "tick"]:
        data = json.dumps({
            "values": [f"aepocraft:{name}"]
        })
        path = os.path.join(function_tags_directory, f"{name}.json")
        write_file(path, data, zipfile)
    

    if zipfile is not None:
        zipfile.close()


build()