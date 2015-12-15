from setuptools import setup

setup(name='uniplaces-aws-scheduler',
      version='1.2',
      description='A scheduling script for aws ec2 instances',
      url='https://github.com/uniplaces/uniplaces-aws-scheduler',
      author='mlimaloureiro',
      author_email='miguel.loureiro@uniplaces.com',
      license='MIT',
      packages=['awsscheduler'],
      install_requires=[
          'docopt',
          'boto'
      ],
      entry_points={
        'console_scripts': 'aws-scheduler=awsscheduler.scheduler:run_cli'
      },
      include_package_data=True,
      zip_safe=False)