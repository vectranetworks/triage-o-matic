## Triage-O-Matic

Triage-O-Matic allows you to automatically create and maintain a triage rule, based on a specific detection and a hostname regular expression.

#### Getting started

There are a few requirements to host and run ToM (Triage-o-Matic):

* A current linux server with current kernel.
* A running version of docker on this server (https://www.docker.com).
* An account on the vectra brain that has the required level of access.

#### Quickstart

1)  First you need to create a local configuration file that will configure ToM when the container starts up.  The
config file should be named triage-o-matic.json and needs to be a properly formatted JSON file.  Here is a sample
configuration file for reference.

    ```{
      "brain" : {
        "url": "brain ip or fqdn",
        "token": "account token value here",
        "triage_category": "what to recategorize the detections as"
      },
    
      "detection": {
        "detection_category": "command & control",
        "detection_type": "Suspect Domain Activity",
        "regular_expression": "iphone",
        "description": "Automatically maintained triage rule, do not edit, delete if necessary"
      },
    
      "triage-o-matic": {
        "interval": 600
      }
    }
    ```
    
    Let's step through the config.  The first section allows you to define the brain that we will be running against.
    
    ## brain object
    The brain object holds the configuration for triage-o-matic, it consists of.
    
    #### url 
    This can be either an IP address, FQDN, or Hostname, as long as it's resolvable within your environment.  Do not
    prefix this with http:// or https://.  Https is the only transport supported for this tool.
    
    ### token 
    Copy and paste the users token that you would like to use to authenticate to the brain.  To get the users token,
    just login to the UI as the account that you would like to use then click on the "My Profile" link.  You will see the
    accounts token under the API Token section.
    
    #### triage_category
    The triage_category set here will be used as the Recategorize detections as value.
    
    ## detection object
    The detection object is where you specify the type of detection that you would like to triage.  It's values consist of
    
    #### detection_category
    
    Must be one of the following values:
    * "botnet activity"
    * "command & control"
    * "reconnaissance"
    * "lateral movement" 
    * "exfiltration".
    
    This should be set to the category of detections you would like to triage.
    
    #### detection_type
    
    The detection_type should be set to the model name that you would like to triage.  For example to triage SDA detections
    set the detection_type value to "Suspect Domain Activity"
    
    #### regular_expression
    
    This value will be tested against all hosts that exhibit the above listed detection type and category.  If the regex value also matches then this host will be triaged.
    This must be a python compatible regex string.  Anything from a simple string to a full regex expression.
    
    #### description
    
    This is the description that will be used for the triage rule.
    
    ### Triage-O-Matic
    
    The only required setting in the triage-o-matic object is the interval.
    
    #### interval
    
    This controls how often ToM will requerry and reprocess the host detections and then update the triage rule.  This
    is specified in seconds.

2)  After you have properly created the triage-o-matic.json file, make sure that it is available and accessible to docker on your docker host.  
We will be using docker bind mounts to make it available to the code within the container.

3)  To run Triage-O-Matic construct a command line such as the following:

```docker container run -v /location/of/my/triage-o-matic.json:/triage-o-matic/config/ vectracraig/triage-o-matic```

This will download triage-o-matic from dockerhub from the vectracraig account.  This is the location where all newer versions of ToM will be made available.

Logs of ToM operation are available via the command 
```docker logs <container id> -f```



