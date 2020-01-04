from setuptools import setup, find_packages

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
    packages=find_packages(),
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    install_requires=['django-jenkins',
                      'django<2.3',
                      'django-errors',
                      'python-social-auth',      #<-- Need By Auth Process: OAuth2 Social
                      'social-auth-app-django',  #<-- Need By Auth Process: OAuth2 Social
                      'django-otp',	 			 #<-- Need By Auth Process: One-Time-Password
                      'django-two-factor-auth',	 #<-- Need By Auth Process: One-Time-Password
                      'django-oauth-toolkit',	 #<-- Need By Auth Process: OAuth2 Token
                      'djangorestframework-jwt', #<-- Need By Auth Process: Token
                      'djangorestframework',	 #<-- Need By Rest API
                      'easy_thumbnails',		 #<-- Need By Imge Cropping
                      'django-image-cropping',
                      'django-user-sessions',	 #<-- Need By Monitor
                      'django-axes',			 #<-- Need By Monitor
                      ],
    tests_require=['runtests.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
