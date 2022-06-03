from setuptools import setup, find_packages

version = '0.1'

setup(name='web_translator',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Epistemonikos',
      author_email='',
      url='epistemonikos.org',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "bottle==0.12.20",
          "bottle-sqlite",
          "language_middleware",
          "mako>=0.4.1",
          "paste",
          "polib",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """
      )
