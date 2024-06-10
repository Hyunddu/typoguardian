from setuptools import setup, find_packages

setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'cython',
        'requests',
        'sentence-transformers',
        'lxml',
        'tqdm',
        'pyxdameraulevenshtein',
        'Pillow',
        'clavier @ git+https://github.com/MaxHalford/clavier',
        'pipdeptree',
        'numpy',
        'jarowinkler'
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
