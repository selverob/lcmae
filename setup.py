from setuptools import setup, find_packages

setup(
    name='evacsim',
    version='0.9',
    description="A simulator for evacuation planning algorithms",
    python_requires=">=3.7.0",
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        evacsim=evacsim.cli:cli
    ''',
)
