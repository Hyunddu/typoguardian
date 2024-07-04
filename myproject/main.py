from myproject.dld import run_dld
from myproject.img_numpy import run_img_numpy
from myproject.clavier import run_clavier
from myproject.jaro import run_jaro
from myproject.mal_compare import run_mal_compare
from myproject.yara_scan import run_yara_scan
from myproject.typos_result_download import run_typos_result_download
from myproject.sbom_analysis import run_sbom_analysis
from myproject.guarddog_analysis import run_guarddog_analysis
import json
import os
import shutil
import concurrent.futures


def clean_existing_data():
    paths_to_clean = ['final_typos.json', 'typos_DLD.json', 'typos_image_numpy.json', 'typos_clavier.json', 'typos_jaro.json', 'comparison_results.json', 'yara_scan_results.json', 'pypi_zip', 'similar_packages', 'packages.zip']
    for path in paths_to_clean:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Removed directory: {path}")
        elif os.path.isfile(path):
            os.remove(path)
            print(f"Removed file: {path}")


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
                penalty = -0.3
            else:
                penalty = 0
            if dld_score >= 0.83:
                bonus = 0.2
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

    with open('final_typos.json', 'w') as file:
        json.dump(final_results, file, indent=4)

    print("Saved: final_typos.json")


def main():
    parser = argparse.ArgumentParser(description="Typosquatting Detection Tool")
    parser.add_argument("--update", action="store_true", help="Update the PyPI package list")
    parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold for detection")
    parser.add_argument("--clean", action="store_true", help="Clean up downloaded files and folders after execution")
    parser.add_argument("package_name", nargs="?", help="Package name (e.g., matplotlib)")
    args = parser.parse_args()

    clean_existing_data()

    if args.update:
        run_dld(None, update=True)
        print("PyPI package list updated. Exiting.")
        return

    if not args.package_name:
        print("Package name is required. Exiting.")
        return

    run_dld(args.package_name, update=args.update, threshold=args.threshold)

    # Run Jaro, Clavier, and Img_Numpy in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_jaro = executor.submit(run_jaro)
        future_clavier = executor.submit(run_clavier)
        future_img_numpy = executor.submit(run_img_numpy)

        concurrent.futures.wait([future_jaro, future_clavier, future_img_numpy], return_when=concurrent.futures.ALL_COMPLETED)

    combine_scores()
    run_typos_result_download()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_sbom = executor.submit(run_sbom_analysis, 'packages.zip', 'packages')
        future_mal_compare = executor.submit(run_mal_compare)
        future_yara_scan = executor.submit(run_yara_scan)
        future_guarddog = executor.submit(run_guarddog_analysis)

        concurrent.futures.wait([future_sbom, future_mal_compare, future_yara_scan, future_guarddog], return_when=concurrent.futures.ALL_COMPLETED)


if __name__ == "__main__":
    main()
