import os
import fastentrypoints

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "README.rst")) as f:
        README = f.read()
    with open(os.path.join(here, "CHANGES.txt")) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ""

setup(
    name="dictknife",
    version=open(os.path.join(here, "VERSION")).read().strip(),
    description="utility set of handling dict",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only"
        # "Programming Language :: Python :: 3.6",
        # "Development Status :: 4 - Beta",
    ],
    keywords="dict, dict-handling",
    author="podhmo",
    author_email="ababjam61@gmail.com",
    url="https://github.com/podhmo/dictknife",
    packages=find_packages(exclude=["dictknife.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    extras_require={
        "testing": ["ruamel.yaml", "jsonpatch"],
        "lint": ["flake8"],
        "docs": ["sphinx", "recommonmark", "sphinx_rtd_theme"],
        "load": ["ruamel.yaml", "tomlkit"],
        "command": ["ruamel.yaml", "magicalimport", "prestring"],
        "spreadsheet": ["google-api-python-client", "google-auth-oauthlib"],
    },
    tests_require=[],
    test_suite="dictknife.tests",
    entry_points="""
      [console_scripts]
      dictknife=dictknife.commands.dictknife:main
      jsonknife=dictknife.commands.jsonknife:main
      swaggerknife=dictknife.commands.swaggerknife:main
""",
)
