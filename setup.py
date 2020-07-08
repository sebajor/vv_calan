import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vv_calan", # Replace with your own username
    version="0.0.1",
    author="Sebastian Jorquera",
    author_email="",
    description="Python package to interface vector voltmeter in ROACH2",
    long_description=long_description,
    long_description_content_type="",
    url="https://github.com/sebajor/vv_calan",
    packages=setuptools.find_packages(),
    package_data={'':['ppc_save*']},
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=2.7',
)
