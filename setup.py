

from setuptools import setup


setup(name="tap-teamwork",
      version="1.0.0",
      description="Singer.io tap for extracting data from teamwork API",
      author="Stitch",
      url="http://singer.io",
      classifiers=["Programming Language :: Python :: 3 :: Only"],
      py_modules=["tap_teamwork"],
      install_requires=[
        "singer-python==5.12.1",
        "requests==2.31.0",
   
      ],
      entry_points="""
          [console_scripts]
          tap-teamwork=tap_teamwork:main
      """,
      packages=["tap-teamwork"],
      package_data = {
          "tap_teamwork": ["schemas/*.json"],
      },
      include_package_data=True,
)