import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="but-edi-parser",
    version="1.16.0",
    author="Steven Athouel",
    author_email="sathouel@gmail.com",
    description="EDI Parser for BUT Suppliers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sathouel/but_edi_parser.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)