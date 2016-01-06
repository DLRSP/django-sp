from setuptools import setup

readme = open('README.md').read()

from django_errors import __version__ as version

setup(
    name="django-sp",
    version=version,
    url='https://github.com/DLRSP/django-sp',
    license='MIT',
    description="Django Custom Social Profile Auth/User",
    author='DLRSP',
    author_email='dlrsp.py@gmail.com',
    packages=['socialprofile', ],
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    install_requires=['django_nose',
                      'pytest-runner',
                      'django>=1.8',
                      'python-social-auth',		#<-- Need By Auth Process
                      'django-errors',
                      ],
    tests_require=['runtests.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP ',
    ]
)
