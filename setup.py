from setuptools import setup, find_packages

install_requires = ['Django', 'djangorestframework']
tests_require = ['pytest', 'pytest-runner>=2.0,<3dev', 'pytest-flake8']

setup(
    name='iron',
    version='0.0.1',
    description="Web based file manager",
    author="Presslabs SRL",
    author_email="ping@presslabs.com",
    url="https://github.com/Presslabs/iron",
    install_requires=install_requires,
    tests_require=tests_require,
    packages=find_packages(exclude=['tests']),
    extras_require={
        'test': tests_require
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)
