""" Python PyPi Setup Configurations """

import setuptools

with open("README.md") as fh:
    long_description = fh.read().strip()

with open('requirements.txt') as fh:
    requirements = fh.read().strip().split('\n')

setuptools.setup(
    name="textflow",
    version="0.4.6",
    author="Yasas",
    author_email="wayasas@gmail.com",
    description="Simple and extensible framework for end to end text based natural language understanding.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ysenarath/textflow",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'textflow = textflow.main:app',
        ],
    },
)
