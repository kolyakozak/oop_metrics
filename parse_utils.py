import ast
import os
import glob
import sys
import logging

logger = logging.getLogger(__name__)


def get_python_files(module_path: str):
    python_files = []

    for file_path in glob.glob(os.path.join(module_path, "**/*.py"), recursive=True):
        python_files.append(file_path)
    return python_files


def get_classes(file):
    classes = []

    tree = ast.parse(file)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node)

    return classes


def parse_module_classes(module_path: str):
    classes = []
    files = get_python_files(module_path)

    for file in files:
        with open(file) as f:
            file_classes = get_classes(f.read())
            classes += file_classes

    classes_dict = {}
    for cls in classes:
        classes_dict[cls.name] = cls

    return classes_dict


def parse_file_classes(file_path: str):
    with open(file_path) as f:
        classes = get_classes(f.read())
    classes_dict = {}
    for cls in classes:
        classes_dict[cls.name] = cls

    return classes_dict