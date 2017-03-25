from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='cgsn_parsers',
      version='0.2.0',
      description=(
          'Collection of parsers for converting raw data from the OOI Endurance, '
          'Global and Pioneer moorings to JSON for further work.'
      ),
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Topic :: Data Parsing :: JSON :: Scientific :: OOI',
      ],
      keywords='OOI Endurance Global Pioneer raw data parsing',
      url='http://github.com/ooi-integration/cgsn-parsers',
      author='Christopher Wingard',
      author_email='cwingard@coas.oregonstate.edu',
      license='MIT',
      packages=['cgsn_parsers'],
      install_requires=[
          'nose',
          'numpy',
          'munch >= 2.1.0',
          'pytz'
      ],
      include_package_data=True,
      zip_safe=False)
