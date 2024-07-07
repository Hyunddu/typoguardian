#pip install argparse pyxdameraulevenshtein pyfiglet requests
import argparse
from pyxdameraulevenshtein import damerau_levenshtein_distance
import re
import requests

MAX_LEVENSHTEIN_DISTANCE = 2

DICTIONARY_PREFIX = [
    'python-', 'python_', 'python.', 'python3-', 'python3_', 'python3.', 'python2-', 'python2_', 'python2.',
    'py-', 'py_', 'py.', 'py3-', 'py3_', 'py3.', 'py2-', 'py2_', 'py2.',
    'pypi-', 'pypi_', 'pypi.',
    'pip-', 'pip_', 'pip.',
    'dev-', 'dev_', 'dev.',
    'alpha-', 'alpha_', 'alpha.',
    'beta-', 'beta_', 'beta.',
    'rc-', 'rc_', 'rc.',
    'final-', 'final_', 'final.',
    'release-', 'release_', 'release.',
    'stable-', 'stable_', 'stable.',
    'unstable-', 'unstable_', 'unstable.',
    'latest-', 'latest_', 'latest.',
    'legacy-', 'legacy_', 'legacy.'
]

DICTIONARY_SUFFIX = [
    '-python', '_python', '.python', '-python3', '_python3', '.python3', '-python2', '_python2', '.python2',
    '-py', '_py', '.py', '-py3', '_py3', '.py3', '-py2', '_py2', '.py2',
    '-pypi', '_pypi', '.pypi',
    '-pip', '_pip', '.pip',
    '-dev', '_dev', '.dev',
    '-alpha', '_alpha', '.alpha',
    '-beta', '_beta', '.beta',
    '-rc', '_rc', '.rc',
    '-final', '_final', '.final',
    '-release', '_release', '.release',
    '-stable', '_stable', '.stable',
    '-unstable', '_unstable', '.unstable',
    '-latest', '_latest', '.latest',
    '-legacy', '_legacy', '.legacy'
]

DICTIONARY_SUBSTITUTIONS = {
    'python': ['python3', 'python2', 'py', 'py3', 'py2'],
    'python3': ['python', 'python2', 'py', 'py3', 'py2'],
    'python2': ['python', 'python3', 'py', 'py2', 'py3'],
    'py': ['python3', 'python', 'python2', 'py3', 'py2'],
    'py3': ['python3', 'python', 'python2', 'py', 'py2'],
    'py2': ['python2', 'python', 'python3', 'py', 'py3']
}

URL_TOP_5000_PACKAGES = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"


def levenshtein_check(package, popular_packages):
    for popular_package in popular_packages:
        if 0 < damerau_levenshtein_distance(package, popular_package) <= MAX_LEVENSHTEIN_DISTANCE:
            return popular_package
    return ''


def prefix_suffix_check(package, popular_packages):
    package = remove_prefix_suffix(package, DICTIONARY_PREFIX, DICTIONARY_SUFFIX)
    result = check_in_popular_packages(package, popular_packages)
    if result:
        return result
    return ''


def prefix_suffix_and_levenshtein_check(package, popular_packages):
    return levenshtein_check(remove_prefix_suffix(package, DICTIONARY_PREFIX, DICTIONARY_SUFFIX), popular_packages)


def substitutions_check(package, popular_packages, dictionary_substitutions):
    for substitution_key in dictionary_substitutions.keys():
        if package.find(substitution_key) != -1:
            for substitution in dictionary_substitutions[substitution_key]:
                package_check = package.replace(substitution_key, substitution)
                result = check_in_popular_packages(package_check, popular_packages)
                if result:
                    return result
    return ''


def permutation_check(package, popular_packages):
    if '-' not in package and '_' not in package and '.' not in package:
        return ''
    else:
        words = re.split('[-_.]', package)
        num_words = len(words)

        def generate(idx):
            if idx == num_words:
                permuted_word_1 = '-'.join(words)
                permuted_word_3 = '_'.join(words)
                permuted_word_2 = '.'.join(words)

                if package != permuted_word_1:
                    result = check_in_popular_packages(permuted_word_1, popular_packages)
                    if result:
                        return result
                if package != permuted_word_2:
                    result = check_in_popular_packages(permuted_word_2, popular_packages)
                    if result:
                        return result
                if package != permuted_word_3:
                    result = check_in_popular_packages(permuted_word_3, popular_packages)
                    if result:
                        return result
                return ''

            for i in range(idx, num_words):
                words[idx], words[i] = words[i], words[idx]
                popular_package = generate(idx + 1)
                if popular_package:
                    return popular_package
                words[idx], words[i] = words[i], words[idx]
            return ''

        return generate(0)


def remove_prefix_suffix(package, dictionary_prefix, dictionary_suffix):
    for word in dictionary_prefix:
        if package.startswith(word):
            package = package[len(word):]
    for word in dictionary_suffix:
        if package.endswith(word):
            package = package[:-len(word)]
    return package


def check_in_popular_packages(package, popular_packages):
    for popular_package in popular_packages:
        if package == popular_package:
            return popular_package
    return ''


def preprocess_package(package):
    package = re.sub(r'[<=>!@~`].*', '', package)
    if package.startswith('#'):
        package = package[1:]
    return package.lower()


def load_packages(file_path):
    try:
        with open(file_path) as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []


def update_popular_packages():
    try:
        response = requests.get(URL_TOP_5000_PACKAGES)
        data = response.json()

        with open("pypi_popular_packages.txt", 'w') as file:
            for entry in data['rows']:
                library_name = entry['project']
                file.write(library_name + '\n')
        print("Data updated in pypi_popular_packages.txt")
    except Exception as e:
        print("An error occurred:", str(e))


def main():
    parser = argparse.ArgumentParser(description="Typosquatting detection tool for Python (PyPi) packages.")
    parser.add_argument("--update", action="store_true", help="Update the popular package list before checking")
    args = parser.parse_args()

    try:
        if args.update:
            update_popular_packages()

        popular_packages = load_packages("pypi_popular_packages.txt")

        while True:
            package = input("Enter a package name (or 'quit' to exit): ").strip().lower()
            if package == 'quit':
                break

            package = preprocess_package(package)
            if not check_in_popular_packages(package, popular_packages):
                first_check = levenshtein_check(package, popular_packages)
                second_check = prefix_suffix_check(package, popular_packages)
                third_check = prefix_suffix_and_levenshtein_check(package, popular_packages)
                fourth_check = substitutions_check(package, popular_packages, DICTIONARY_SUBSTITUTIONS)
                fifth_check = permutation_check(package, popular_packages)

                if first_check or second_check or third_check or fourth_check or fifth_check:
                    correct_package = first_check or second_check or third_check or fourth_check or fifth_check
                    print(f"The package '{package}' may be affected by Typosquatting.")
                    print(f"Maybe you meant the package '{correct_package}'?")
                else:
                    print(f"No similar popular package found for '{package}'.")
            else:
                print(f"'{package}' is a valid popular package.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
