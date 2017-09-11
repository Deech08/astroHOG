from setuptools import setup

setup(name='astroHOG',
      version='0.1',
      description='AstroHOG is set of tools for the study of correlations using the Histograms of Oriented Gradients',
      url='https://github.com/Deech08/astroHOG',
      author='Juan Diego Soler, Dhanesh Krishnarao (DK)',
      author_email='soler@mpia.de, krishnarao@astro.wisc.edu',
      license='MIT',
      packages=['astroHOG'],
      install_requires=[
          'numpy',
          'astropy',
          'scipy',
          'matplotlib',
          'reproject'
      ],
      include_package_data=True,
      zip_safe=False)
