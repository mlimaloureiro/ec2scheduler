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
import boto.ec2.elb
import sys,os,json,logging, datetime, time

config = SafeConfigParser()

aws_access_key = None
aws_secret_key = None
aws_region = None
 
def init():
    # Setup AWS connection
    aws_access_key = config.get('aws','access_key','')
    aws_secret_key = config.get('aws','secret_key','')
    aws_region = config.get('aws', 'region','')

    global ec2
    ec2 = boto.ec2.connect_to_region(
            region_name = aws_region,
            aws_access_key_id = aws_access_key,
            aws_secret_access_key = aws_secret_key)

def run(args):
    config.read([args['--config'], 'aws.cfg'])
    init()

if __name__ == "__main__":
    args = docopt(__doc__, version='AWS 1.0.1')
    # We have valid args, so run the program.
    run(args)