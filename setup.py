from setuptools import setup, find_packages

requirements = [
    "setuptools",
    "setuptools_scm",
    "docker",
    "psutil",
]

setup(
    name='msconvert',
    author="Falk Boudewijn Schimweg",
    author_email='git@falk.schimweg.de',
    python_requires='>=3.10',
    use_scm_version=True,
    requirements=requirements,
    packages=find_packages(include=['msconvert', 'msconvert.*']),
    setup_requires=['setuptools_scm'],
    entry_points={
        'console_scripts': [
            'msconvert=msconvert.__cli:main',
        ],
    },
)