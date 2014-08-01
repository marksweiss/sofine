import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup    


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'sofine',
    version = '0.1',
    author = 'Mark S. Weiss',
    author_email = 'marksimonweiss@gmail.com',
    description = ('Lightweight framework for creating data-collection plugins and chaining together calls to them, from CLI, REST or Python'),
    license = 'MIT',
    keywords = 'glueAPI data pipelines scraper webAPI',
    url = 'http://packages.python.org/sofine',
    packages=['sofine'],
    long_description=read('README.md'),
    'install_requires'=['mechanize', 'beautifulsoup4', 'ystockquote']
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ],
)
