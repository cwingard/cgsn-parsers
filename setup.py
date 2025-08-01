from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('VERSION.txt') as f:
        return f.read().strip()


setup(name='cgsn_parsers',
      version=version(),
      description=(
          'Collection of parsers for converting raw data from the OOI Endurance, '
          'Global and Pioneer moorings to JSON for further work.'
      ),
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.10',
          'Topic :: Data Parsing :: JSON :: Scientific :: OOI',
      ],
      keywords='OOI Endurance Global Pioneer raw data parsing',
      url='https://bitbucket.org/ooicgsn/cgsn-parsers',
      author='Christopher Wingard',
      author_email='chris.wingard@oregonstate.edu',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'nose',
          'numpy',
          'munch >= 2.1.0',
          'pandas',
          'pytz'
      ],
      include_package_data=True,
      zip_safe=False)
