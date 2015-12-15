# Uniplaces AWS Scheduler

The AWS Scheduler is a script that given a set of profiles schedule the uptime of ec2 instances.

## Getting Started

Install through pip.

    pip install uniplaces-aws-scheduler

The initial configuration is done in the `aws.conf` file. Copy the `aws.conf.dist`
to `aws.conf` and configure with the right credentials.
By default `aws.conf` reads schedule profiles from `scheduler.json` but you can change
the directory from where you want to load the profiles.

To run the scheduler just run

    aws-scheduler -c path/to/config_file

#### Profiles

The scheduler expects you to create profiles to start and stop the machines.

You can just copy the `scheduler.json.dist` and start creating your new profiles from there.

```
{
    "profiles": [ // an array of profiles
        {
            "name": "staging", // profile name
            "region": "us-west-1", // aws region
            "schedule": { // weekday schedule
                "monday": {
                    "start": 9, // start hour
                    "stop": 19 // stop hour
                },
                "tuesday": {
                    "start": 9,
                    "stop": 19
                },
                "wednesday": {
                    "start": 9,
                    "stop": 19
                },
                "thursday": {
                    "start": 9,
                    "stop": 19
                },
                "friday": {
                    "start": 9,
                    "stop": 19
                },
                "saturday": {
                    "start": 9,
                    "stop": 19
                },
                "sunday": {
                    "start": 9,
                    "stop": 19
                }
            },
            "instance_tags": [ // tags from the instances you want to attach this profile schedule
                "jobs-staging", // this tag should be the name of the instance tag:Name
                "admin-staging",
                "reports-staging"
            ],
            "elb_names": [ // add this configuration if you want to reregister this elb instances
                "example-tag-elb-name"
            ]
        }
    ]
}
```

