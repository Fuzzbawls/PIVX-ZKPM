from setuptools import setup, find_packages
from codecs import open
from os import path
import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
from distutils.util import get_platform

setup(
    name='ZkParamsWizard',
    version='0.0.1',
    description='',
    author='fuzzbawls',
    author_email='a@b.c',
    license='MIT',
    url='https://www.pivx.org',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
    ],
    keywords='',
    install_requires=[
        'requests >= 2.18.4',
        'tqdm == 4.48.0',
    ] + (
        ['pyqt5 >= 5.9.0'] if get_platform() == 'linux-x86_64' else []
    ),
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ZkParamsWizard = ZkParamsWizard.zkparamswizard:run',
        ]
    },
    python_requires='>=3'
)
