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
        'console_scripts': [
            'conanVsIntegration-integrate=conan_vs_integration.integrate:main',
            'conanVsIntegration-install=conan_vs_integration.install:main'],
        },
      include_package_data=True,
      zip_safe=False)
