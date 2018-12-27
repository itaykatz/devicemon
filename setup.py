from setuptools import setup, find_packages

setup(
    name='devicemon.py',
    version='0.1.15',
    packages=find_packages(),
    author='Itay Katz',
    scripts=['devicemon.py'],
    install_requires=[
        "tqdm >= 4.28.1",
        "Click >= 7.0",
        "setuptools >= 40.2.0",
        "pandas >= 0.23.4",
        "Flask >= 1.0.2",
        "pytest >= 4.0.2",
        "flaskr "
    ]

)
