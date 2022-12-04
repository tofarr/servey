import setuptools

from servey.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {
    "dev": ["black"],
    "server": [
        "starlette~=0.19",
        "strawberry-graphql~=0.125",
        "uvicorn~=0.18",
        "pygments~=2.13",
        "requests~=2.28",
        "python-multipart~=0.0",
    ],
    "scheduler": ["celery~=5.2"],
    "aws": [
        "boto3~=1.26",
    ],
    "serverless": [
        "pyyaml~=6.0",
        "ruamel.yaml~=0.17",
        "strawberry-graphql~=0.125",  # We need this to generate the graphql schema - or do we?
    ],
}
extras_require["all"] = list(
    {
        dependency
        for dependencies in extras_require.values()
        for dependency in dependencies
    }
)


setuptools.setup(
    name="servey",
    version=__version__,
    author="Tim O'Farrell",
    author_email="tofarr@gmail.com",
    description="A better API layer for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tofarr/servey",
    packages=setuptools.find_packages(exclude=("tests",)),
    package_data={"": ["*.html", "*.js", "*.css", "*.yml"]},
    include_package_data=True,
    install_requires=[
        "marshy~=3.0",
        "schemey~=5.4",
        "pyjwt~=2.4",
        "cryptography~=37.0",
    ],
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
