from setuptools import setup

setup(
    name='baku',
    version='0.1',
    py_modules=['baku'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        baku=baku:cli
    ''',
)
