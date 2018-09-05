import vectra
import logging
import re
import json
import requests
import os
import sys
import time
# triage-o-matic start
print('waiting 60 seconds')
time.sleep(60)

def looper():
    logging.debug('triage rule {} already exists moving into maintenance mode'.format(triage_category))
    logging.debug('reading rule to grab list of all hosts.')
    rule_response = vc.get_rules(name=description)
    logging.debug('rule_response is {}'.format(rule_response))
    hosts_in_triage_rule = rule_response['host']
    logging.debug('hosts_in_triage_rule is {}'.format(hosts_in_triage_rule))

    # I am in the maintenance loop here
    while True:
        logging.debug('At top of maintenance mode loop.')
        all_hosts_with_detections = []
        filtered_hosts_with_detections = []
        filtered_host_ids_with_detections = []
        updated_hosts_with_detections = []
        transformed_hosts_with_detections = []
        existing_hosts_in_triage_rule = []

        # This is the sleep counter between updates.

        for count in range(config_file['triage-o-matic']['interval']):
            logging.debug('times through delay loop {}/{}'.format(count, interval))
            time.sleep(1)

        logging.debug('timer elapsed, retrieving current triage rule named {}'.format(description))
        existing_triage_rule_response = vc.get_rules(name=description)
        existing_hosts_in_triage_rule = existing_triage_rule_response['host']
        logging.debug('the triage rule currently consists of these hosts {} for a total of {} entries'
                      .format(existing_hosts_in_triage_rule, len(existing_hosts_in_triage_rule)))

        logging.debug('retrieving the current list of detections')
        try:
            detections_response = vc.get_detections(detection_type=detection_type)
            logging.debug('successfully received detections list')

        except:

            logging.error('unable to receive the detections list')
        # I have the list now to process it.

        logging.debug('Here is the list of hosts that have a detection of detection type {}'.format(detection_type))
        for host in range(len(detections_response.json()['results'])):
            all_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])

        logging.debug(
            'hosts exhibiting the detection type {}.  For a total of {} hosts'.format(all_hosts_with_detections,
                                                                                      len(all_hosts_with_detections)))
        logging.debug('filtering based on the chosen regex of {}'.format(regular_expression))

        logging.debug('starting to test patterns. . .')
        pattern = re.compile(regular_expression, re.IGNORECASE)
        for host in range(len(detections_response.json()['results'])):
            logging.debug(
                'testing pattern - {}'.format(detections_response.json()['results'][host]['src_host']['name']))
            match = pattern.search(detections_response.json()['results'][host]['src_host']['name'])
            if match is not None:
                filtered_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])
                filtered_host_ids_with_detections.append(detections_response.json()['results'][host]['src_host']['id'])

        logging.debug('list of filtered hosts with detections {}'.format(filtered_hosts_with_detections))
        logging.debug('list of filtered host ids with detections {}'.format(filtered_host_ids_with_detections))

        transformed_hosts_with_detections = vc._transform_hosts(filtered_host_ids_with_detections)
        logging.debug('transformed hosts with detections {}'.format(transformed_hosts_with_detections))
        logging.debug('testing all hosts with detections against the hosts in the current triage rule')

        for host in transformed_hosts_with_detections:
            if host in existing_hosts_in_triage_rule:
                logging.debug('found host {} in list existing_hosts_in_triage_rule'.format(host))

            elif host not in existing_hosts_in_triage_rule:
                logging.debug('host {} NOT FOUND in list existing_hosts_in_triage_rule'.format(host))
                existing_hosts_in_triage_rule.append(host)

        logging.debug('additional hosts to be added to triage rule are {} total of {}'
                      .format(existing_hosts_in_triage_rule, len(existing_hosts_in_triage_rule)))

        response = vc.update_rule(name=description, host=existing_hosts_in_triage_rule)
        logging.debug(response)


with open('config/triage-o-matic.json') as config_object:
    config_file = json.load(config_object)
    logging_level = config_file['triage-o-matic']['log_level']
    print(logging_level)

    if logging_level == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('triage-o-matic set to DEBUG logging')

    elif logging_level == 'INFO':
        logging.basicConfig(level=logging.INFO)
        logging.info('triage-o-matic set to INFO logging')

    else:
        logging.basicConfig(level=logging.ERROR)

#extracing the config file values and setting internal variables

brain_url = config_file['brain']['url']
url = 'https://' + brain_url
logging.debug('url set to {}'.format(url))

token = config_file['brain']['token']
logging.debug('token set to {}'.format(token))

triage_category = config_file['brain']['triage_category']
logging.debug('triage_category set to {}'.format(triage_category))

detection_category = config_file['detection']['detection_category']
detection_type = config_file['detection']['detection_type']
description = config_file['detection']['description']
is_whitelist = False
regular_expression = config_file['detection']['regular_expression']
interval = config_file['triage-o-matic']['interval']



logging.debug('detection_category set to {}'.format(detection_category))
logging.debug('detection_type set to {}'.format(detection_type))
logging.debug('description set to {}'.format(description))
logging.debug('is_whitelist set to {}'.format(is_whitelist))
logging.debug('interval set to {}'.format(interval))
all_hosts_with_detections = []
filtered_hosts_with_detections = []
filtered_host_ids_with_detections = []
hosts_in_triage_rule = []


try:
    logging.debug('creating Vectra client object')
    vc = vectra.VectraClient(url=url, token=token)

except:
    logging.critical('unable to create the Vectra client object, unable to continue')
    sys.exit(1)

logging.debug('determining if the triage rule currently exists.')
rule = vc.get_rules(name=description)
if rule is None:

    logging.debug('triage rule {} does not exist, creating. . .'.format(description))



    logging.debug('querying list of detections from brain at url {}'.format(url))

    try:
        detections_response = vc.get_detections(detection_type=detection_type)
        logging.debug('successfully received detections list')

    except:
        logging.error('unable to receive the detections list')

    logging.debug('Here is the list of hosts that have a detection of detection type {}'.format(detection_type))
    for host in range(len(detections_response.json()['results'])):
        all_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])

    logging.debug('hosts exhibiting the detection type {}.  For a total of {} hosts'.format(all_hosts_with_detections, len(all_hosts_with_detections)))
    logging.debug('filtering based on the chosen regex of {}'.format(regular_expression))

    logging.debug('starting to test patterns. . .')
    pattern = re.compile(regular_expression, re.IGNORECASE)
    for host in range(len(detections_response.json()['results'])):
        logging.debug('testing pattern - {}'.format(detections_response.json()['results'][host]['src_host']['name']))
        match = pattern.search(detections_response.json()['results'][host]['src_host']['name'])
        if match is not None:
            filtered_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])
            filtered_host_ids_with_detections.append(detections_response.json()['results'][host]['src_host']['id'])

    logging.debug('list of filtered hosts with detections {}'.format(filtered_hosts_with_detections))
    logging.debug('list fo filtered host ids with detections {}'.format(filtered_host_ids_with_detections))

    create_rule_response = vc.create_rule(detection_category=detection_category, detection_type=detection_type, triage_category=triage_category,
                   description=description, is_whitelist=False, host=filtered_host_ids_with_detections)
    logging.debug(create_rule_response.json())

    looper()


if rule is not None:
    looper()





# The list all_hosts_with_detections consists of all the hostnames.



# The time has elapsed now retrieving all detections of the proper detection type.
#
#         try:
#             detections_response = vc.get_detections(detection_type=detection_type)
#             logging.debug('successfully received detections list')
#
#         except:
#
#             logging.error('unable to receive the detections list')
#
# # I have the list now to process it.
#
#         logging.debug('Here is the list of hosts that have a detection of detection type {}'.format(detection_type))
#         for host in range(len(detections_response.json()['results'])):
#             all_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])
# # The list all_hosts_with_detections consists of all the hostnames.
#
#         logging.debug('hosts exhibiting the detection type {}.  For a total of {} hosts'.format(all_hosts_with_detections, len(all_hosts_with_detections)))
#         logging.debug('filtering based on the chosen regex of {}'.format(regular_expression))
#
#         logging.debug('starting to test patterns. . .')
#         pattern = re.compile(regular_expression, re.IGNORECASE)
#         for host in range(len(detections_response.json()['results'])):
#             logging.debug('testing pattern - {}'.format(detections_response.json()['results'][host]['src_host']['name']))
#             match = pattern.search(detections_response.json()['results'][host]['src_host']['name'])
#             if match is not None:
#                 filtered_hosts_with_detections.append(detections_response.json()['results'][host]['src_host']['name'])
#                 filtered_host_ids_with_detections.append(detections_response.json()['results'][host]['src_host']['id'])
#
#         logging.debug('list of filtered hosts with detections {}'.format(filtered_hosts_with_detections))
#         logging.debug('list of filtered host ids with detections {}'.format(filtered_host_ids_with_detections))
#
#         logging.debug('transforming the list of host ids')
#
#         transformed_hosts_with_detections = vc._transform_hosts(filtered_host_ids_with_detections)
#
#         logging.debug('transformed hosts with detections {}'.format(transformed_hosts_with_detections))
#         logging.debug('comparing host list to determine any differences')
#
#         for host in



# All stuff here


# with open('config/triage-o-matic.json') as config_object:
#     config_data = json.load(config_object)
# log_level = config_data['triage-o-matic']['log_level']
#
# if log_level == 'DEBUG':
#     logging.basicConfig(level=logging.DEBUG)
#     logger = logging.getLogger(__name__)
#     logger.debug('logging level set to DEBUG')
#
# elif log_level == 'INFO':
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
#     logger.info('logging level set to INFO')
#
#
# logger.info('Starting triage-o-matic')
# logger.debug('opening and reading the Triage-O-Matic config object.')
# logger.debug('this was read from the config object {}'.format(config_data))
#
# # This is where I am extracting all the values from the config object and setting internal variables.
# detection_category = config_data['detection']['detection_category']
# detection_type = config_data['detection']['detection_type']
# brain_url = config_data['brain']['url']
# url = 'http://{}'.format(brain_url)
# token = config_data['brain']['token']
# regular_expression = config_data['detection']['regex']
# triage_rule_name = config_data['brain']['triage_rule_name']
#
# logger.debug('triage-o-matic is managing the triage rule named {}'.format(triage_rule_name))
#
#
# vc = vectra.VectraClient(url=url, token=token)
# logger.debug('checking for the existence of triage rule named {}'.format(triage_rule_name))
# try:
#     response = vc.get_rules(name='SDA : iPhone Rule')
#
# except AttributeError:
#     logger.debug('triage rule does not exist.')


# Set up the regex matching based on the pattern in the config object
# pattern = re.compile(regular_expression, re.IGNORECASE)




# logger.debug('requesting hosts from the brain.')
# try:
#     response = vc.get_hosts()
#
# except(IOError, EOFError, OSError):
#     logger.debug('There has been a serious error when communicating with the brain.', exc_info=True)

#
# detections_response = vc.get_detections(detection_type=detection_type)
# detections = detections_response.json()
# # logger.debug(detections_response.json())
#
# logger.debug('Here is the list of hosts that have a detection of detection type {}'.format(detection_type))
# for host in range(len(detections['results'])):
#     logger.debug(detections['results'][host]['src_host']['name'])
#
# logger.debug('filerting returned hosts by supplied regex.')
# extracted_hostnames = []
# extracted_hostids = []
#
# logger.debug('starting to test patterns. . .')
# for host in range(len(detections['results'])):
#     logger.debug('testing pattern - {}'.format(detections['results'][host]['src_host']['name']))
#     match = pattern.search(detections['results'][host]['src_host']['name'])
#     if match is not None:
#         extracted_hostnames.append(detections['results'][host]['src_host']['name'])
#         extracted_hostids.append(detections['results'][host]['src_host']['id'])
#
# logger.debug('filtered hosts {}'.format(extracted_hostnames))
# logger.debug('filtered host ids {}'.format(extracted_hostids))
# transformed_hosts = vc._transform_hosts(extracted_hostids)
# logger.debug('tranformed set {}'.format(transformed_hosts))
#
# # If the list extracted_hostnames is empty
# if not extracted_hostnames:
#     logger.debug('Result set is empty.  Please check the settings and regex.')
#     sys.exit(1)
#
# # if not then we can create the triage rule.
#
# logger.debug('Creating triage rule named {}'.format(extracted_hostnames))
#
# logger.debug('calling create_rule / detection_category={} - detection_type={} - triage_category={} - host={} - description={}'
#              .format(detection_category, detection_type, triage_rule_name,extracted_hostids,triage_rule_name))
#
# vc.create_rule(detection_category=detection_category, detection_type=detection_type, triage_category=triage_rule_name,
#                description='This is ToM Test, its only a test', is_whitelist=False, host=transformed_hosts)
#


# triage_json = {
#     "detection_category": detection_category,
#     "triage_category": triage_rule_name,
#     "detection": detection_type,
#     "description": "Test, Someone should come up with a better description :)",
#     "host": extracted_hostids,
#     "all_hosts": "false",
#     "is_whitelist": "false",
# }
#

# vc.create_rule(detection_category=detection_category,detection_type=detection_type, triage_category=triage_rule_name,
#                description='This is a test', is_whitelist=False, host=extracted_hostids)

# auth_headers = {'Authorization': 'Token {}'.format(token)}
# triage_url = url + '/api/v2/rules'

# response = requests.post(triage_url, headers=auth_headers, json=triage_json, verify=False)
# print(response.json())



# hosts = response.json()
#
# logger.debug('counting returned hostnames')
# number_of_hosts = len(hosts['results'])
# logger.debug('number of hosts {}'.format(number_of_hosts))
#
# logger.debug('hostnames found:')
#
# for host in range(len(hosts['results'])):
#     logger.debug(hosts['results'][host]['name'])
#
# logger.debug('searching for hostnames that contain the string iphone')
# search_pattern = re.compile('iphone', re.IGNORECASE)
#
# for host in range(len(hosts['results'])):
#     match = search_pattern.search(hosts['results'][host]['name'])
#     if match is not None:
#         logger.debug(hosts['results'][host]['name'])