from setuptools import setup

readme = open('README.md').read()

from django_errors import __version__ as version

setup(
    name="django-socialprofile",
    version=version,
    url='https://github.com/DLRSP/django-socialprofile',
    license='MIT',
    description="Django Custom Social Profile Auth/User",
    author='Davide La Rosa',
    author_email='davide.larosa.coins@gmail.com',

    packages=['socialprofile', ],
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    install_requires=['pytest-runner',
                      'django>=1.8',
                      'python-social-auth==0.2.1',		#<-- Need By Auth Process
	],
    tests_require=['runtests.py'],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: BTC :: BitCoin :: 500 :: 400 :: errors',
    ]
)
