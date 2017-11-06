from setuptools import setup

setup(name='conan_vs_integration',
      version='0.1',
      description='',
      url='',
      author='Jeroen_de_vlieger',
      author_email='jeroen.devlieger@nikon.com',
      license='',
      packages=['conan_vs_integration'],
      entry_points = {
        'console_scripts': ['conanVsIntegration=conan_vs_integration.command_line:main'],
        },
      zip_safe=False)
