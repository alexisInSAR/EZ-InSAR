from setuptools import setup

setup(
    name='doris',
    version='5.0.3',
    packages=['install', 'doris_stack', 'doris_stack.functions', 'doris_stack.main_code', 'prepare_stack'],
    url='https://github.com/TUDelftGeodesy/Doris',
    license='LICENSE.txt',
    author='Gert Mulder',
    author_email='g.mulder-@tudelft.nl',
    description='doris InSAR processing software',
    install_requires=['osr', 'fastkml']
)
