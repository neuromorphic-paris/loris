import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='loris',
    version='0.1.0',
    url='https://github.com/neuromorphic-paris/loris',
    author='Gregor Lenz',
    author_email='gregor.lenz@inserm.fr',
    description='python3 library to handle event-based files',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
