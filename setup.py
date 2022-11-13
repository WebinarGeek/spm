from setuptools import setup

setup(
    name="spm",
    version="0.1.0",
    author="WebinarGeek",
    description="The lightweight Screen Procfile Manager",
    license="MIT",
    py_modules=["spm"],
    include_package_data=True,
    python_requires=">= 3.7.*",
    setup_requires=["setuptools"],
    entry_points={"console_scripts": ["spm= spm:main"]}
)
