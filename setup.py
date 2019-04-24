from setuptools import setup, find_packages

setup(
    name='evacsim',
    version='0.9',
    description="A simulator for evacuation planning algorithms",
    python_requires=">=3.7.0",
    packages=find_packages(),
    install_requires=[dep.strip() for dep in open("requirements.txt").readlines()],
    entry_points='''
        [console_scripts]
        evacsim=evacsim.cli:cli
    ''',
)
