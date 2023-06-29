import ast
import os
import glob
import sys
import logging

logger = logging.getLogger(__name__)

def get_class_dit(cls_obj, classes):
    if not isinstance(cls_obj, ast.ClassDef) or len(cls_obj.bases) == 0:
        return 0
    dits = [get_class_dit(classes[b.id], classes) + 1 for b in cls_obj.bases if 'id' in b.__dict__.keys() and b.id in classes.keys()]
    if len(dits) == 0:
        return 0
    return max(dits)


def get_class_nc(cls_obj, classes):
    children = []
    for c in classes.values():
        for b in c.bases:
            if (isinstance(b, ast.Name) and b.id == cls_obj.name) or (isinstance(b, ast.Attribute) and 'id' in b.__dict__.keys() and b.id == cls_obj.attr):
                children.append(b.id)
    return len(children)

def get_methods(cls_obj):
    methods = set()
    for body in cls_obj.body:
        if isinstance(body, ast.FunctionDef):
            methods.add(body.name)
    return methods

def get_inherited_methods(cls_obj, classes):
    bases = __get_bases(cls_obj, classes)
    inherited_methods = set()
    for base in bases:
        for body in base.body:
            if isinstance(body, ast.FunctionDef):
                inherited_methods.add(body.name)
    return inherited_methods




def get_inherited_not_overriden_methods(cls_obj, classes):
    methods = get_methods(cls_obj)
    inherited_methods = get_inherited_methods(cls_obj, classes)
    return inherited_methods - methods

def get_inherited_and_overriden_methods(cls_obj, classes):
    methods = get_methods(cls_obj)
    inherited_methods = get_inherited_methods(cls_obj, classes)
    return inherited_methods.intersection(methods)

def get_new_methods(cls_obj, classes):
    methods = get_methods(cls_obj)
    inherited_methods = get_inherited_methods(cls_obj, classes)
    return methods -inherited_methods

def get_all_methods(cls_obj, classes):
    methods = get_methods(cls_obj)
    inherited_methods = get_inherited_methods(cls_obj, classes)
    methods.update(inherited_methods)
    return methods

def get_visible_methods(cls_obj):
    methods = get_methods(cls_obj)
    hidden_methods = get_hidden_methods(cls_obj)
    return methods - hidden_methods

def get_hidden_methods(cls_obj):
    hidden_methods = set()
    for body in cls_obj.body:
        if isinstance(body, ast.FunctionDef):
            
            if body.name.startswith('_'):
                hidden_methods.add(body.name)
    return hidden_methods



def get_attributes(cls_obj):
    attributes = set()
    for body in cls_obj.body:
        if isinstance(body, ast.FunctionDef):
            if body.name.endswith('_'):
                for attr in body.body:
                    if isinstance(attr, ast.Assign) and isinstance(attr.targets[0], ast.Attribute):
                        value = attr.targets[0].attr
                        attributes.add(value)

    return attributes

def get_inherited_attributes(cls_obj, classes):
    bases = __get_bases(cls_obj, classes)
    inherited_attributes = set()
    attributes = get_attributes(cls_obj)
    for base in bases:
        for body in base.body:
            if isinstance(body, ast.FunctionDef):
                if body.name.startswith('_'):
                    for attr in body.body:
                        if isinstance(attr, ast.Assign) and isinstance(attr.targets[0], ast.Attribute):
                            value = attr.targets[0].attr
                            if not value.startswith('__'):
                                inherited_attributes.add(value)

                    continue
    return inherited_attributes

def get_hidden_attributes(cls_obj):
    hidden_attributes = set()
    for body in cls_obj.body:
        if isinstance(body, ast.FunctionDef):
            if body.name.endswith('_'):
                for attr in body.body:
                    if isinstance(attr, ast.Assign) and isinstance(attr.targets[0], ast.Attribute):
                        value = attr.targets[0].attr
                        if value.startswith('__'):
                            hidden_attributes.add(value)
    return hidden_attributes



def get_inherited_not_overriden_attributes(cls_obj, classes):
    attributes = get_attributes(cls_obj)
    inherited_attributes = get_inherited_attributes(cls_obj, classes)
    return inherited_attributes - attributes

def get_all_attributes(cls_obj, classes):
    attributes = get_attributes(cls_obj)
    inherited_attributes = get_inherited_attributes(cls_obj, classes)
    attributes.update(inherited_attributes)
    return attributes


def __get_bases(cls_obj, classes):
    bases = []
    for base in cls_obj.bases:
        if isinstance(base, ast.Name) and base.id in classes.keys():
            bases.append(classes[str(base.id)])
            bases += __get_bases(
                classes[str(base.id)], classes)

    return bases

def calculate_mhf(visible_methods_lens, hidden_methods_lens):
    Mv_sum = sum([visible_methods_lens[idx] + hidden_methods_lens[idx] for idx in range(len(visible_methods_lens))])
    Mh_sum = sum(hidden_methods_lens)
    try:
        return Mh_sum / Mv_sum
    except ZeroDivisionError as e:
        return 0

def calculate_ahf(hidden_attributes_lens, all_attributes_lens):
    Ah_sum = sum(hidden_attributes_lens)
    Ad_sum = sum(all_attributes_lens)
    try:
        return Ah_sum / Ad_sum
    except ZeroDivisionError as e:
        return 0

def calculate_pof(inherited_overriden_methods_lens, new_methods_lens, noc):
    Mo_sum = sum(inherited_overriden_methods_lens)
    Mn_sum = sum([new_methods_lens[idx]*noc[idx] for idx in range(len(noc))])
    try:
        return Mo_sum / Mn_sum
    except ZeroDivisionError as e:
            return 0

def calculate_mif(inherited_not_overriden_methods_lens, all_methods_lens):
    Mi_sum = sum(inherited_not_overriden_methods_lens)
    Ma_sum = sum(all_methods_lens)
    try:
        return Mi_sum / Ma_sum
    except ZeroDivisionError as e:
        return 0

def calculate_aif(inherited_not_overriden_attributes_lens, all_attributes_lens):
    Ai_sum = sum(inherited_not_overriden_attributes_lens)
    Aa_sum = sum(all_attributes_lens)
    try:
        return Ai_sum / Aa_sum
    except ZeroDivisionError as e:
        return 0