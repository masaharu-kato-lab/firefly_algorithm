from setuptools import setup, find_packages

setup(
    name='firefly_algorithm_src',
    version='1.0.0',
    url='https://github.com/masaharu-kato-lab/firefly_algorithm',
    author='Masaharu Kato',
    author_email='saa01068@gmail.com',
    description='Implementation of firefly algorithm',
    packages=find_packages(),    
    install_requires=['mypy', 'pytest', 'matplotlib'],
)
