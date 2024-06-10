from myproject.dld import run_dld
from myproject.img_numpy import run_img_numpy
from myproject.clavier import run_clavier
from myproject.jaro import run_jaro
import argparse
import json


def combine_scores():
    try:
        with open('typos_DLD.json', 'r') as file:
            dld_data = json.load(file)
    except FileNotFoundError:
        print("typos_DLD.json not found.")
        return

    try:
        with open('typos_image_numpy.json', 'r') as file:
            image_data = json.load(file)
    except FileNotFoundError:
        print("typos_image_numpy.json not found.")
        return

    try:
        with open('typos_clavier.json', 'r') as file:
            clavier_data = json.load(file)
    except FileNotFoundError:
        print("typos_clavier.json not found.")
        return

    try:
        with open('typos_jaro.json', 'r') as file:
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
                penalty = 0.3
            else:
                penalty = 0
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] -= penalty
            else:
                combined_results[package][typo] = penalty

    for package in image_data:
        for typo, image_score in image_data[package]:
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += 1.5 * image_score

    for package in jaro_data:
        for typo, jaro_score in jaro_data[package]:
            if package in combined_results and typo in combined_results[package]:
                combined_results[package][typo] += jaro_score

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

    with open('final_typos.json', 'w') as file:
        json.dump(final_results, file, indent=4)

    print("Combined results saved in final_typos.json")


def main():
    parser = argparse.ArgumentParser(description="Typosquatting Detection Tool")
    parser.add_argument("--update", action="store_true", help="Update the PyPI package list")
    parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold for detection")
    parser.add_argument("package_name", nargs="?", help="Package name (e.g., matplotlib)")
    args = parser.parse_args()

    if args.update:
        run_dld(None, update=True)
        print("PyPI package list updated. Exiting.")
        return

    if not args.package_name:
        print("Package name is required. Exiting.")
        return

    run_dld(args.package_name, update=args.update, threshold=args.threshold)
    run_img_numpy()
    run_clavier()
    run_jaro()
    combine_scores()


if __name__ == "__main__":
    main()
