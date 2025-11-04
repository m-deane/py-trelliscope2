"""Setup script for py-trelliscope."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="py-trelliscope",
    version="0.1.0",
    description="Interactive visualization displays for exploring collections of plots",
    author="py-trelliscope contributors",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "viz": ["matplotlib>=3.0", "plotly>=5.0"],
        "all": ["matplotlib>=3.0", "plotly>=5.0"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
