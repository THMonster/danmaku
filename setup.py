import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="danmaku",
    version="0.0.1",
    author="IsoaSFlus",
    author_email="me@isoasflus.com",
    description="A python package for getting danmaku of some streaming site",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IsoaSFlus/danmaku",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    python_requires='>=3.7',
)
