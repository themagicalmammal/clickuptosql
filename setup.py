import codecs
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    LONG_DESCRIPTION = "\n" + fh.read()

VERSION = "1.0.0"
DESCRIPTION = "Replicate ClickUp Database using Excel."

with open("requirements.txt") as f:
    required = f.read().splitlines()

# Setting up
setup(
    name="clickuptosql",
    version=VERSION,
    author="Dipan Nanda",
    author_email="d19cyber@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/themagicalmammal/clickuptosql",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    install_requires=required,
    project_urls={
        # "Website": "https://github.com/themagicalmammal/clickuptosql",
        # "Source code": "https://github.com/themagicalmammal/clickuptosql",
        "Documentation":
        "https://github.com/themagicalmammal/clickuptosql/blob/main/README.md",
        "Bug tracker":
        "https://github.com/themagicalmammal/clickuptosql/issues",
    },
    keywords=["python", "ClickUp", "Excel", "pandas"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
)
