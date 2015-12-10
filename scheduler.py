"""This scheduler starts/stops EC2 instances using a JSON based schedule.
 
Usage:
  scheduler (-h | --help)
  scheduler --version
 
Options:
  -c --config CONFIG    Use alternate configuration file [default: ./aws.cnf].
  -h --help             Show this screen.
  --version             Show version.
"""

from docopt import docopt
from ConfigParser import SafeConfigParser
import boto.ec2
import sys,os,json, datetime, time

config = SafeConfigParser()
 
def init():
    # Setup AWS connection
    global ec2_eu
    global ec2_us
    ec2_eu = connect_from_conf('aws_eu')
    ec2_us = connect_fromt_conf('aws_us')

    print ec2_eu
    print ec2_us

def connect_from_conf(aws_conf):
    aws_access_key = config.get(aws_conf,'access_key','')
    aws_secret_key = config.get(aws_conf,'secret_key','')
    aws_region = config.get(aws_conf, 'region','')

    return boto.ec2.connect_to_region(
            region_name = aws_region,
            aws_access_key_id = aws_access_key,
            aws_secret_access_key = aws_secret_key)

def run(args):
    config.read([args['--config'], 'aws.conf'])
    init()

if __name__ == "__main__":
    args = docopt(__doc__, version='scheduler 1.0')
    # We have valid args, so run the program.
    run(args)