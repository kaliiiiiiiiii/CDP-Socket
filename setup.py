import setuptools


requirements = ['aiohttp', 'websockets', "orjson"]

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cdp-socket',
    author='Aurin Aegerter',
    author_email='aurinliun@gmx.ch',
    description='socket for handling chrome-developer-protocol connections',
    keywords='Chromium,socket, webautomation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kaliiiiiiiiii/CDP-Socket',
    project_urls={
        'Documentation': 'https://github.com/kaliiiiiiiiii/CDP-Socket',
        'Bug Reports':
            'https://github.com/kaliiiiiiiiii/CDP-Socket/issues',
        'Source Code': 'https://github.com/kaliiiiiiiiii/CDP-Socket',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP :: Browsers'

    ],
    python_requires='>=3.7',
    license="MIT",
    install_requires=requirements,
    include_package_data=True,
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
)
