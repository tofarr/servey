import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {
    "dev": [
        "black~=23.3",
        "boto3~=1.26",
        "pytest~=7.2",
        "pytest-cov~=4.0",
        "pytest-xdist~=3.2",
        "pylint~=2.17",
    ],
    "server": [
        "starlette~=0.19",
        "strawberry-graphql~=0.151",
        "uvicorn[standard]~=0.18",
        "pygments~=2.13",
        "requests~=2.28",
        "python-multipart~=0.0",
    ],
    "scheduler": ["celery~=5.2"],
    "serverless": [
        "pyyaml~=6.0",
        "ruamel.yaml~=0.17",
        "strawberry-graphql~=0.177",  # We need this to generate the graphql schema - or do we?
    ],
    "web_page": [
        "Jinja2~=3.1",
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
    author="Tim O'Farrell",
    author_email="tofarr@gmail.com",
    description="A better API layer for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tofarr/servey",
    packages=setuptools.find_packages(
        exclude=("tests*", "servey_main*", "static_site", "examples")
    ),
    package_data={"": ["*.html", "*.js", "*.css", "*.yml"]},
    include_package_data=True,
    install_requires=[
        "cryptography~=37.0",
        "json-urley~=1.0",
        "marshy~=4.0",
        "pyjwt~=2.4",
        "python-dateutil~=2.8",
        "schemey~=6.0",
    ],
    extras_require=extras_require,
    setup_requires=["setuptools-git-versioning"],
    setuptools_git_versioning={"enabled": True, "dirty_template": "{tag}"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
