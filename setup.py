from setuptools import setup, find_packages

with open("README.md") as file:
    long_description = file.read()

setup(
    name="regex_hir",
    description="Alternative regular expression module, to replace re.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.1.1",
    license="MIT",
    author="Dexter Hill",
    packages=find_packages("regex_hir"),
    package_dir={"": "regex_hir"},
    url="https://github.com/DexterHill0/regex_hir",
    keywords="regex python syntax ast",
    install_requires=[
        "unicategories==0.1.1",
    ],
)
