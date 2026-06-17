from setuptools import setup, find_packages

setup(
    name="tap-teamwork",
    version="0.2.0",
    description="Singer.io tap for extracting data from Teamwork API",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_teamwork"],
    install_requires=[
        "singer-python==6.8.0",
        "requests==2.33.1",
        "backoff==2.2.1"
    ],
    entry_points="""
        [console_scripts]
        tap-teamwork=tap_teamwork:main
    """,
    packages=find_packages(),
    package_data={
        "tap_teamwork": ["schemas/*.json"]
    },
    include_package_data=True,
)
