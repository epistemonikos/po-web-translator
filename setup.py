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
          "bottle==0.9.6", "lxml", "webtest>=1.3.1", "language_middleware", "mako>=0.4.1", "paste", "babel", "oauth2", "polib"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """
      )
