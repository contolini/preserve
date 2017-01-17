# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='codepreserve',
    version='1',
    description='A project to preserve the public\'s code',
    long_description=long_description,
    url='https://github.com/codepreserve/preserve',
    author='Will Barton',
    author_email='g@gulielmus.com',
    license='BSD2',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'click',
        'requests',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['tox', 'pytest', 'pytest-cov', 'flake8'],
    },
    setup_requires=[
        'pytest-runner',
    ],
    entry_points={
        'console_scripts': [
            'preserve=preserve.command_line:main',
        ],
    },
)
