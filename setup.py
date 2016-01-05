from setuptools import setup

setup(name='aws-ec2-scheduler',
      version='1.0',
      description='A scheduling script for aws ec2 instances',
      url='https://github.com/mlimaloureiro/ec2scheduler',
      author='mlimaloureiro',
      author_email='mdiasloureiro@gmail.com',
      license='MIT',
      packages=['ec2scheduler'],
      install_requires=[
          'docopt',
          'boto'
      ],
      entry_points={
        'console_scripts': 'ec2scheduler=ec2scheduler.scheduler:run_cli'
      },
      include_package_data=True,
      zip_safe=False)
