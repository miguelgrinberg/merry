"""
merry
-----
Decorator based error handling.
"""

from setuptools import setup


version = open('__version__').read().strip()

setup(
    name='merry',
    version=version,
    url='http://github.com/miguelgrinberg/merry/',
    license='MIT',
    author='Miguel Grinberg',
    author_email='miguelgrinberg50@gmail.com',
    description='Decorator based error parsing',
    long_description=__doc__,
    py_modules=['merry'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    tests_require=[
        'coverage'
    ],
    test_suite='test_merry',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
