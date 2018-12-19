import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='Lemuras',
    version='1.1.7',
    author='AivanF.',
    author_email='projects@aivanf.com',
    description='A small Python library to deal with big tables',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AivanF/Lemuras',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Topic :: Utilities',
        'Topic :: Text Processing',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: Freely Distributable',
    ],
)
