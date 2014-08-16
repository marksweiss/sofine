import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup    


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'sofine',
    version = '0.2.1',
    author = 'Mark S. Weiss',
    author_email = 'marksimonweiss@gmail.com',
    maintainer = 'Mark S. Weiss',
    maintainer_email = 'marksimonweiss@gmail.com',
    description = ('Lightweight framework for creating data-collection plugins and chaining together calls to them, from CLI, REST or Python'),
    license = 'MIT',
    keywords = 'glueAPI data pipelines scraper webAPI',
    url = 'http://packages.python.org/sofine',
    packages=['sofine', 'sofine.lib', 'sofine.lib.utils', 'sofine.plugins', 'sofine.plugins.example',  'sofine.plugins.mock', 'sofine.plugins.standard', 'sofine.tests'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ]
)
