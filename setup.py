from setuptools import setup, find_packages

setup(
    name="tap-teamwork",
    version="1.0.0",
    description="Singer.io tap for extracting data from Teamwork API",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_teamwork"],
    install_requires=[
        "singer-python==6.1.1",
        "requests==2.32.4",
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
