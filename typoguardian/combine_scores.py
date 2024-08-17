import json
import os

current_script_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(current_script_path))
output_file = os.path.join(BASE_DIR, 'final_typos.json')


def combine_scores():
    try:
        file_path = os.path.join(BASE_DIR, 'typos_DLD.json')
        with open(file_path, 'r') as file:
            dld_data = json.load(file)
    except FileNotFoundError:
        print("typos_DLD.json not found.")
        return

    try:
        file_path = os.path.join(BASE_DIR, 'typos_image_numpy.json')
        with open(file_path, 'r') as file:
            image_data = json.load(file)
    except FileNotFoundError:
        print("typos_image_numpy.json not found.")
        return

    try:
        file_path = os.path.join(BASE_DIR, 'typos_clavier.json')
        with open(file_path, 'r') as file:
            clavier_data = json.load(file)
    except FileNotFoundError:
        print("typos_clavier.json not found.")
        return

    try:
        file_path = os.path.join(BASE_DIR, 'typos_jaro.json')
        with open(file_path, 'r') as file:
            jaro_data = json.load(file)
    except FileNotFoundError:
        print("typos_jaro.json not found.")
        return

    combined_results = {}

    for package in dld_data:
        combined_results[package] = {}
        for typo, dld_score in dld_data[package]:
            combined_results[package][typo] = dld_score
            if dld_score < 0.75:
                penalty = -0.3
            else:
                penalty = 0
            if dld_score >= 0.83:
                bonus = 0.2
            elif dld_score >= 0.8:
                bonus = 0.1
            else:
                bonus = 0
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += penalty + bonus
            else:
                combined_results[package][typo] = penalty + bonus

    for package in image_data:
        for typo, image_score in image_data[package]:
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += 1.5 * image_score

    for package in jaro_data:
        for typo, jaro_score in jaro_data[package]:
            if jaro_score >= 0.9:
                bonus = 0.3
            elif jaro_score >= 0.85:
                bonus = 0.2
            else:
                bonus = 0
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += jaro_score + bonus

    for package in clavier_data:
        for typo, clavier_score in clavier_data[package]:
            if clavier_score < 2:
                bonus = 0.5
            else:
                bonus = 0
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += bonus
            else:
                combined_results[package][typo] = bonus

    final_results = {}
    for package in combined_results:
        final_results[package] = sorted(combined_results[package].items(), key=lambda x: x[1], reverse=True)

    with open(output_file, 'w') as file:
        json.dump(final_results, file, indent=4)

    print("Saved: final_typos.json")
