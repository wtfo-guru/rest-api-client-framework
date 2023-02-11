from setuptools import setup, find_packages

with open('README.md','r') as r:
    long_description = r.read()

setup(
    name='gawsoft_api_client',
    version='1.0.0',
    packages=find_packages(),
    namespace_packages=['gawsoft'],
    author="Gawsoft.pl",
    author_email="biuro@gawsoft.pl",
    description="Rest Api Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gawsoftpl/rest-api-client-framework-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source Code": "https://github.com/gawsoftpl/rest-api-client-framework-python",
    },
    licence="MIT",
    install_requires=[
        x.strip()
        for x in open('requirements.txt').readlines()
        if x and not x.startswith('#')
    ],
    python_requires='>=3.8',
)