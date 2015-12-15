#!/usr/bin/env python

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
import boto.ec2.elb
import sys, os, json, datetime, time

config = SafeConfigParser()
ec2_conn = {}
elb_conn = {}

def run(args):
  """ Run the script

      Args:
        args: CLI arguments.
  """
  config.read([args['--config'], 'aws.conf'])
  init(args)

  while True:
    schedule()
    time.sleep(3600)

def init(args):
  """ Setup initial configuration and connections

  Args:
    args: CLI arguments.
  """
  # Setup AWS connection
  aws_eu = connect_from_conf('aws_eu')
  aws_us = connect_from_conf('aws_us')
  ec2_conn['eu-west-1'] = aws_eu['ec2']
  elb_conn['eu-west-1'] = aws_eu['elb']
  ec2_conn['us-west-1'] = aws_us['ec2']
  elb_conn['us-west-1'] = aws_us['elb']
  global schedules
  schedules = get_schedules()

def connect_from_conf(aws_conf):
  """ Connect to ec2 and elb region

    Args:
      aws_conf: aws credentials

    Returns:
      Dict with ec2 and elb connection object for region
  """
  aws_access_key = config.get(aws_conf,'access_key','')
  aws_secret_key = config.get(aws_conf,'secret_key','')
  aws_region = config.get(aws_conf, 'region','')

  return {
    'ec2':
      boto.ec2.connect_to_region(
      region_name = aws_region,
      aws_access_key_id = aws_access_key,
      aws_secret_access_key = aws_secret_key),
    'elb':
      boto.ec2.elb.connect_to_region(
      region_name = aws_region,
      aws_access_key_id = aws_access_key,
      aws_secret_access_key = aws_secret_key)
  }

def get_schedules():
  """ Read schedule configuration from file and load the json.

      Returns:
        Dict with the configuration
  """
  path = config.get('schedule', 'paths', './schedule.json')
  with open(path) as schedule_file:
    return json.load(schedule_file)

def schedule():
  """ Check all schedule configurations to start and stop instances """
  for profile in schedules['profiles']:
    instances = _get_instances(profile['instance_tags'], profile['region'])
    start_stop_instances(instances, profile['schedule'])
    reregister_elb_instances(profile)

def _get_instances(instance_tags, region):
  """ Get boto ec2 instance objects by provided tags

      Args:
        instance_tags: the tags associated with the instances
        region: aws region

      Returns:
        An array of boto ec2 instance objects
  """
  return ec2_conn[region].get_all_instances(filters={"tag:Name": instance_tags})

def start_stop_instances(instances, schedule):
  """ Start and stop the instances given a schedule

      Args:
        instances: An array of reservations containing.
        schedule: key value with days and start/stop time.
  """
  for reservation in instances:
    for instance in reservation.instances:
      region = instance.placement
      if instance.state == 'running' and _get_desired_state(schedule) == 'stop':
        print "Should stop " + instance.id + "."
        instance.stop()
      elif instance.state == 'stopped' and _get_desired_state(schedule) == 'start':
        print "Should start " + instance.id + "."
        instance.start()
      else:
        print "Nothing to do."

def _get_desired_state(schedule):
  """ Find the desired state give a schedule

      Args:
        schedule: dict with days and start/stop time.

      Returns:
        A string with the desired state. (start/stop)
  """
  current_hour = int(time.strftime("%H", time.gmtime()))
  current_week_day = time.strftime("%A", time.gmtime()).lower()
  start = schedule[current_week_day]['start']
  stop = schedule[current_week_day]['stop']

  state = 'stop'
  if current_hour >= start and current_hour < stop:
    state = 'start'

  return state

def reregister_elb_instances(profile):
  """ ELB does not send health checks after stopping/starting
      the instance. This method reregister the instances in the
      profile ELB's to start sending health checks again.

      Args:
        profile: dict with profile configuration.
  """
  if 'elb_names' in profile:
    conn = elb_conn[profile['region']]
    elbs = conn.get_all_load_balancers(profile['elb_names'])
    for elb in elbs:
      instance_ids = _get_instance_ids(elb.instances)
      print "Reregistering " + elb.name + " instances."
      conn.deregister_instances(elb.name, instance_ids)
      conn.register_instances(elb.name, instance_ids)
      # to avoid elb rate limit throttling
      time.sleep(1)

def _get_instance_ids(instances):
  """ Given an array of boto.ec2.instances returns
      instance ids.

      Args:
        instances: boto.ec2.instances

      Returns:
        Array of string instance ids
  """
  instance_ids = []
  for instance in instances:
    instance_ids.append(instance.id)
  return instance_ids

def run_cli():
  args = docopt(__doc__, version='scheduler 1.2.2')
  # We have valid args, so run the program.
  run(args)

if __name__ == "__main__":
  args = docopt(__doc__, version='scheduler 1.2.2')
  # We have valid args, so run the program.
  run(args)

