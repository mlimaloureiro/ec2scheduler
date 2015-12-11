"""This scheduler starts/stops EC2 instances using a JSON based schedule.
 
Usage:
  scheduler [options]
  scheduler (-h | --help)
  scheduler --version
 
Options:
  -c --config CONFIG     Use alternate configuration file [default: ./aws.cnf].
  -h --help              Show this screen.
  --version              Show version.
"""

from docopt import docopt
from ConfigParser import SafeConfigParser
import boto.ec2
import sys, os, json, datetime, time

config = SafeConfigParser()
ec2 = {}

def init(args):
    # Setup AWS connection
    ec2['eu-west-1'] = connect_from_conf('aws_eu')
    ec2['us-west-1'] = connect_from_conf('aws_us')
    global schedules
    schedules = get_schedules()

def connect_from_conf(aws_conf):
    aws_access_key = config.get(aws_conf,'access_key','')
    aws_secret_key = config.get(aws_conf,'secret_key','')
    aws_region = config.get(aws_conf, 'region','')

    return boto.ec2.connect_to_region(
            region_name = aws_region,
            aws_access_key_id = aws_access_key,
            aws_secret_access_key = aws_secret_key)

def get_schedules():
  path = config.get('schedule', 'paths', './schedule.json')
  with open(path) as schedule_file:
    return json.load(schedule_file)

def schedule():
  for profile in schedules['profiles']:
    instances = get_instances(profile['instance_tags'], profile['region'])
    start_stop_instances(instances, profile['schedule'])

def start_stop_instances(instances, schedule):
  for reservation in instances:
    for instance in reservation.instances:
      if instance.state == 'running' and get_desired_state(schedule) == 'stop':
        print "should stop " + instance.id
      elif instance.state == 'stopped' and get_desired_state(schedule) == 'start':
        print "should start " + instance.id
      else:
        print "nothing to do."

def get_desired_state(schedule):
  current_hour = int(time.strftime("%H", time.gmtime()))
  current_week_day = time.strftime("%A", time.gmtime()).lower()
  start = schedule[current_week_day]['start']
  stop = schedule[current_week_day]['stop']

  state = 'stop'
  if current_hour >= start and current_hour <= stop:
    state = 'start'

  return state

def get_instances(instance_tags, region):
  """ Get boto ec2 instance objects by provided tags

      Args:
        instance_tags: the tags associated with the instances
        region: aws region

      Returns:
        An array of boto ec2 instance objects
  """
  return ec2[region].get_all_instances(filters={"tag:Name": instance_tags})

def run(args):
    config.read([args['--config'], 'aws.conf'])
    init(args)
    schedule()

if __name__ == "__main__":
    args = docopt(__doc__, version='scheduler 1.0')
    # We have valid args, so run the program.
    run(args)
