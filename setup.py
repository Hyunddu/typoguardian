from setuptools import setup, find_packages

setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'urllib3',
        'certifi',
        'idna',
        'requests',
        'lxml',
        'tqdm',
        'Cython==3.0.10',
        'pyxdameraulevenshtein',
        'clavier @ git+https://github.com/MaxHalford/clavier',
        'Pillow',
        'pipdeptree',
        'numpy',
        'jarowinkler',
        'yara-python'
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
