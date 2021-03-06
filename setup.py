#!/usr/bin/env python
from __future__ import annotations

import setuptools

setuptools.setup(
    name='bestmobabot',
    version='3.4.0b2',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    description='Hero Wars game bot 🏆',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eigenein/bestmobabot',
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={
        '': ['*'],
    },
    python_requires='>=3.8',
    install_requires=[
        'click',
        'numpy',
        'pandas',
        'pydantic',
        'pyyaml',
        'requests',
        'scikit-learn',
        'scipy',
        'ipython',
        'loguru',
        'beautifulsoup4',
    ],
    tests_require=['pytest'],
    extras_require={},
    entry_points={
        'console_scripts': [
            'bestmobabot = bestmobabot.__main__:main',
            'bestmobabot.trainer = bestmobabot.trainer:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'License :: Free for non-commercial use',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Games/Entertainment',
    ],
    zip_safe=True,
)
