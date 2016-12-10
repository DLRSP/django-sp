from setuptools import setup

readme = open('README.md').read()

from socialprofile import __version__ as version

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
    install_requires=['django-jenkins',
                      'django<1.9',
                      'python-social-auth',      #<-- Need By Auth Process
                      'django-errors',
                      'easy_thumbnails',		 #<-- Need By Imge Cropping
                      'django-image-cropping',
                      ],
    tests_require=['runtests.py'],
    classifiers=[
        'Development Status :: 5 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
