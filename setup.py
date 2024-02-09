from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    desc = fd.read()

setup(
    name="SQLiteHint",
    version="1.0.19",
    description="Have a easier SQLite with helpful methods and readable syntax with sqlitehint.",
    long_description=desc,
    long_description_content_type="text/markdown",
    license_file="LICENSE.txt",
    author="awolverp",
    author_email="awolverp@gmail.com",
    url="https://github.com/awolverp/sqlitehint/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Github": "https://github.com/awolverp/sqlitehint/",
        "Bug Tracker": "https://github.com/awolverp/sqlitehint/issues/new",
    },
    packages=["sqlitehint"],
    package_data={"sqlitehint": ["dbapi.pyi"]},
    include_package_data=True,
)
