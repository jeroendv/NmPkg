from setuptools import setup

setup(name='NmPackage',
      version='0.1',
      description='',
      url='',
      author='Jeroen_de_vlieger',
      author_email='jeroen.devlieger@nikon.com',
      license='',
      packages=['NmPackage'],
      entry_points = {
        'console_scripts': [
            'NmPkg-add=NmPackage.cli.AddPackage:main',
            'NmPkg-install=NmPackage.cli.install:main',
            'NmPkg-list=NmPackage.cli.list:main'],
        },
      include_package_data=True,
      zip_safe=False)
