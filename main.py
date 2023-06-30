import ast
import os
import glob
import sys
import logging
from metric_utils import *
from parse_utils import *

logger = logging.getLogger(__name__)



def calculate_metrics(classes):
    metrics = {}

    all_dits = []
    all_ncs = []
    all_methods_lens = []
    inherited_not_overriden_methods_lens = []
    inherited_and_overriden_methods_lens = []
    hidden_methods_lens = []
    visible_methods_lens = []
    new_methods_lens = []

    attributes_lens = []
    all_attributes_lens = []
    inherited_not_overriden_attributes_lens = []
    hidden_attributes_lens = []

    for cls_name, cls_obj in classes.items():

        dit = get_class_dit(cls_obj, classes)
        nc = get_class_nc(cls_obj, classes)

        all_methods_len = len(get_all_methods(cls_obj, classes))
        inherited_not_overriden_methods_len = len(get_inherited_not_overriden_methods(cls_obj, classes))
        inherited_and_overriden_methods_len = len(get_inherited_and_overriden_methods(cls_obj, classes))
        hidden_methods_len = len(get_hidden_methods(cls_obj))
        visible_methods_len = len(get_visible_methods(cls_obj))
        new_methods_len = len(get_new_methods(cls_obj, classes))

        attributes_len = len(get_attributes(cls_obj))
        all_attributes_len = len(get_all_attributes(cls_obj, classes))
        inherited_not_overriden_attributes_len = len(get_inherited_not_overriden_attributes(cls_obj, classes))
        hidden_attributes_len = len(get_hidden_attributes(cls_obj))

        all_dits.append(dit)
        all_ncs.append(nc)
        all_methods_lens.append(all_methods_len)
        inherited_not_overriden_methods_lens.append(inherited_not_overriden_methods_len)
        inherited_and_overriden_methods_lens.append(inherited_and_overriden_methods_len)
        hidden_methods_lens.append(hidden_methods_len)
        visible_methods_lens.append(visible_methods_len)
        new_methods_lens.append(new_methods_len)

        attributes_lens.append(attributes_len)
        all_attributes_lens.append(all_attributes_len)
        inherited_not_overriden_attributes_lens.append(inherited_not_overriden_attributes_len)
        hidden_attributes_lens.append(hidden_attributes_len)

        metrics[cls_name] = {
            "DIT": dit, # max length from root class to leaf class
            "NC": nc, # number of immediate children of class 
            "MIF": calculate_mif([inherited_not_overriden_methods_len], [all_methods_len]),
            "AIF": calculate_aif([inherited_not_overriden_attributes_len], [all_attributes_len]),
            "MHF": calculate_mhf([visible_methods_len], [hidden_methods_len]),
            "AHF": calculate_ahf([hidden_attributes_len], [attributes_len]),
            "POF": calculate_pof([inherited_and_overriden_methods_len], [new_methods_len], [nc])
        }

    metrics["TOTAL METRICS"] = {
        "MAX_DIT": max(all_dits), # max length from root class to leaf class
        "MAX_NC": max(all_ncs), # number of immediate children of class 
        "MIF": calculate_mif(inherited_not_overriden_methods_lens, all_methods_lens),
        "AIF": calculate_aif(inherited_not_overriden_attributes_lens, all_attributes_lens),
        "MHF": calculate_mhf(visible_methods_lens, hidden_methods_lens),
        "AHF": calculate_ahf(hidden_attributes_lens, attributes_lens),
        "POF": calculate_pof(inherited_and_overriden_methods_lens, new_methods_lens, all_ncs)
    }

    return metrics

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error("Required command arguments missing: <method> <path>")
        exit(1)

    method = sys.argv[1]


    if method == "file":
        classes = parse_file_classes(sys.argv[2])
    elif method == "module":
        classes = parse_module_classes(sys.argv[2])
    else:
        logger.error("Undefined method, available_methods: file, directory, module")
        exit(1)


    results = calculate_metrics(classes)

    output_file = open("OUTPUT.TXT", "w")
    sys.stdout = output_file

    for name, metrics in results.items():
        if name == "TOTAL METRICS":
            print(name, *[f"{metric_name}: {metric_value:.2f}" for metric_name, metric_value in metrics.items()], sep="\n")
            print()

    for name, metrics in results.items():
        if name != "TOTAL METRICS":
            print(name, *[f"{metric_name}: {metric_value:.2f}" for metric_name, metric_value in metrics.items()], sep="\n")
            print()