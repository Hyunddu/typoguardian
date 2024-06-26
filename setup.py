from setuptools import setup, find_packages
import sys
import subprocess
    
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
        'logging',
        'pygments'
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
