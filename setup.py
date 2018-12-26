from setuptools import setup

setup(name='pymage_size',
    version='1.0.0',
    description='A package for getting the dimensions of an image without loading it into memory. No external dependencies.',
    long_description='''
        pymage_size is a small package that enables one to retrieve the dimensions of a number of different image formats
        without the need for extensive libraries like Pillow. It has no external dependencies, making it ideal for inclusion
        in projects that can't afford or simply don't want to have large dependency trees for a simple feature.
        ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Graphics',
        ],
    keywords='image metadata size dimensions',
    url='https://github.com/kobaltcore/pymage_size',
    author='kobaltcore',
    author_email='cobaltcore@yandex.com',
    license='MIT',
    packages=['pymage_size'],
    # install_requires=[],
    include_package_data=True,
    zip_safe=True
)
