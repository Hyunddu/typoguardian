import json
import os
import requests
import zipfile
import re
import shutil

SAVE_DIR = "similar_packages"
PYPI_ZIP_DIR = "pypi_zip"
SIMILAR_JSON_FILE = "final_typos.json"


def get_github_url(package_info):
    project_urls = package_info["info"]["project_urls"]
    if project_urls:
        return next((url for url in project_urls.values() if "github.com" in url), None)
    return None


def get_github_release_url(github_url):
    match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
    if not match:
        return None
    owner, repo = match.groups()
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {
        # 'Authorization': 'git token',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(releases_url, headers=headers)
        response.raise_for_status()
        release_info = response.json()
        tag_name = release_info['tag_name']
        return f"https://github.com/{owner}/{repo}/archive/refs/tags/{tag_name}.tar.gz"
    except requests.exceptions.RequestException:
        return None


def download_package(package_name, version, save_path):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        try:
            download_url = next(
                release['url'] for release in data['urls']
                if release['packagetype'] == 'sdist'
            )
        except StopIteration:
            # If no sdist found on PyPI, try GitHub
            github_url = get_github_url(data)
            if github_url:
                download_url = get_github_release_url(github_url)
            else:
                return False
        response = requests.get(download_url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {package_name}=={version}: {str(e)}")
        return False


def compress_to_zip(base_save_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_save_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_save_path)
                zipf.write(file_path, arcname)
    print(f"Compressed {base_save_path} to {zip_path}")


def get_package_version(package_name):
    try:
        version_url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(version_url)
        response.raise_for_status()
        version_data = response.json()
        return version_data['info']['version']
    except requests.exceptions.RequestException:
        print(f"Failed to fetch version for {package_name}")
        return None


def process_package(package_name, base_save_path):
    version = get_package_version(package_name)
    if version:
        save_path = os.path.join(base_save_path, package_name, version, f"{package_name}-{version}.tar.gz")
        download_package(package_name, version, save_path)


def restructure_dir(package_name, package_type='normal'):
    package_dir = os.path.join(PYPI_ZIP_DIR, package_name)
    if not os.path.exists(package_dir):
        return

    versions = os.listdir(package_dir)
    if not versions:
        return

    for version in versions:
        source_path = os.path.join(package_dir, version)
        if os.path.isdir(source_path):
            if package_type == 'normal':
                target_path = os.path.join(SAVE_DIR, package_name, 'normal', version)
            else:
                target_path = os.path.join(SAVE_DIR, package_type, 'malregistry', package_name, version)

            os.makedirs(target_path, exist_ok=True)

            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(target_path, item)
                shutil.move(s, d)

            # 원본 디렉토리가 비었으면 삭제
            if not os.listdir(source_path):
                os.rmdir(source_path)


def load_similar_packages(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def run_typos_result_download():
    json_file_path = 'final_typos.json'
    base_save_path = 'pypi_zip'
    zip_path = 'packages.zip'

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for norm_pkg_name, package_group in data.items():
        process_package(norm_pkg_name, base_save_path)
        for package_info in package_group:
            package_name, score = package_info
            if score >= 3.0:
                process_package(package_name, base_save_path)
    compress_to_zip(base_save_path, zip_path)

    similar_packages = load_similar_packages(SIMILAR_JSON_FILE)
    for norm_pkg_name, mal_pkg_list in similar_packages.items():
        restructure_dir(norm_pkg_name)
        for mal_pkg in mal_pkg_list:
            mal_pkg_name, score = mal_pkg
            if score >= 3.0:
                restructure_dir(mal_pkg_name, package_type=norm_pkg_name)


if __name__ == '__main__':
    run_typos_result_download()
