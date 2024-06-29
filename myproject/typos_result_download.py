import json
import os
import requests
import zipfile
import re


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
    headers = {'User-Agent': 'Mozilla/5.0'}
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
        # print(f"Failed to download {package_name}=={version}: {str(e)}")
        return False


def compress_to_zip(base_save_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_save_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_save_path)
                zipf.write(file_path, arcname)
    print(f"Compressed {base_save_path} to {zip_path}")


def run_typos_result_download():
    json_file_path = 'final_typos.json'
    base_save_path = 'pypi_zip'
    zip_path = 'packages.zip'

    with open(json_file_path, 'r') as file:
        data = json.load(file)
    for package_group in data.values():
        for package_info in package_group:
            package_name = package_info[0]
            score = package_info[1]
            if score >= 3.0:
                try:
                    version_url = f"https://pypi.org/pypi/{package_name}/json"
                    response = requests.get(version_url)
                    response.raise_for_status()
                    version_data = response.json()
                    version = version_data['info']['version']
                except requests.exceptions.RequestException:
                    continue
                save_path = os.path.join(base_save_path, package_name, version, f"{package_name}-{version}.tar.gz")
                download_package(package_name, version, save_path)
    compress_to_zip(base_save_path, zip_path)


if __name__ == '__main__':
    run_typos_result_download()
