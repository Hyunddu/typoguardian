from setuptools import setup, find_packages
import sys
import subprocess

# Check for Microsoft Visual C++ Build Tools
try:
    subprocess.check_call(['cl'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
except (OSError, subprocess.CalledProcessError):
    print("Microsoft Visual C++ 14.0 or greater is required. Get it with 'Microsoft C++ Build Tools':")
    print("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    sys.exit(1)
    
setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'cython',
        'urllib3',
        'certifi',
        'idna',
        'requests',
        'lxml',
        'tqdm',
        'pyxdameraulevenshtein',
        'Pillow',
        'pipdeptree',
        'numpy',
        'jarowinkler',
        'logging'
    ],
    entry_points={
        'console_scripts': [
            'myproject=myproject.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
