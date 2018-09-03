import os
import fastentrypoints

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

install_requires = []

docs_extras = [
    "sphinx",
    "recommonmark",
    "sphinx_rtd_theme",
]

load_extras = [
    "PyYAML",
    "toml",
]

spreadsheet_extrs = [
    "google-api-python-client",
    "oauth2client",
]

command_extras = [
    "PyYAML",
    "magicalimport",
    "prestring",
]

tests_require = []

testing_extras = tests_require + [
    "PyYAML",
]

setup(
    name='dictknife',
    version='0.8.2',
    description='utility set of handling dict',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords='dict, dict-handling',
    author="podhmo",
    author_email="ababjam61@gmail.com",
    url="https://github.com/podhmo/dictknife",
    packages=find_packages(exclude=["dictknife.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        'docs': docs_extras,
        'load': load_extras,
        'command': command_extras,
        'spreadsheet': spreadsheet_extrs,
    },
    tests_require=tests_require,
    test_suite="dictknife.tests",
    entry_points="""
      [console_scripts]
      dictknife=dictknife.commands.dictknife:main
      jsonknife=dictknife.commands.jsonknife:main
      swaggerknife=dictknife.commands.swaggerknife:main
"""
)
