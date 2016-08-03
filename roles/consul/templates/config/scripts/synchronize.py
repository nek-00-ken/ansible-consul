#!{{ virtualenv_dir }}/bin/python

import ConfigParser
from optparse import OptionParser
import requests
import base64
import json
import os.path
import logging
import glob
from subprocess import Popen, PIPE

# initialize global logger
logger = logging.getLogger('sync')
logger.setLevel(logging.DEBUG)

# Class for catalog actions
class ConsulCatalog():
    def __init__(self, url, port, version):
        self._url = "http://%s:%s/%s" % (url, port, version)
        self._kv = "%s/kv/" % self._url

    def get_kv(self, key):
        logger.info("get_kv : %s" % self._kv + key)
        r = requests.get(self._kv + key)
        logger.info("status code = " + str(r.status_code))
        logger.info("raw content = " + str(r.content))
        return json.loads(str(base64.b64decode(str(json.loads(r.content)[0]['Value'])).decode()))

# Functions
def sync(filepath, content):
    """
     . filepath : a full path a file (including the filename), containing a JSON object
     . content : a python dict
    """
    logger.info("Synchronize file : %s" % filepath)

    if os.path.isfile(filepath):
        with open(filepath) as file:
            if json.load(file) == content:
                logger.info('--> ALREADY OK')
                return 0
            logger.info('CHANGED')
            exit_code = 1
    else:
        logger.info('--> CREATION')
        exit_code = 2

    f = open(filepath, 'w')
    f.write(json.dumps(content))
    f.close()

    return exit_code

def main():

    # parse arguments
    my_parser = OptionParser()
    my_parser.add_option("-c", "--config", dest="config_file", help="(mandatory) path to config file")
    (options, args) = my_parser.parse_args()

    # mandatory arguments
    if not options.config_file:
        my_parser.error('You must specify a path to config')
    config_file = options.config_file
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    # configure logger
    hdlr = logging.FileHandler(config.get('LOGGER', 'filename'))
    hdlr.setFormatter(logging.Formatter(config.get('LOGGER', 'format')))
    logger.addHandler(hdlr)

    # constants
    __SERVICE_NAME__ =      config.get('DEFAULT', 'service_name')
    __CONFIG_DIR__ =        config.get('DEFAULT', 'config_dir')
    __CONSUL_SERVER_IP__ =  config.get('DEFAULT', 'consul_server_ip')
    __WEB_UI_PORT__ =       config.get('DEFAULT', 'web_ui_port')
    __CATALOG_VERSION__ =   config.get('DEFAULT', 'catalog_version')

    # variables
    restart = False

    # 1) get definition from KV store
    logger.info('get definition from KV store')
    catalog = ConsulCatalog(__CONSUL_SERVER_IP__, __WEB_UI_PORT__, __CATALOG_VERSION__)
    raw_def = catalog.get_kv("definitions/services/%s" % __SERVICE_NAME__)

    # 2) update service definition
    service_def = {
        'service': {
            'name': raw_def['service']['name'],
            'port': raw_def['service']['port'],
            'tags': raw_def['service']['tags']
        }
    }
    logger.info('update service definition with : ' + str(service_def))
    restart = True if sync("%s/service_%s.json" % (__CONFIG_DIR__, __SERVICE_NAME__), service_def) is not 0 else restart

    # 3) update checks definitions (id is used for filename: check_{id}.json)
    actual_checks_paths = []
    for check in raw_def['service']['checks']:
        check_id = check['id']
        logger.info("update check definition : check_%s" % str(check_id))
        path = "%s/check_%s.json" % (__CONFIG_DIR__, check['id'])
        restart = True if sync(path, {'check' : check}) is not 0 else restart
        actual_checks_paths.append(path)

    # 4) purge other checks
    list = glob.glob(__CONFIG_DIR__ + '/check_*')
    for path in list:
        if path not in actual_checks_paths:
            logger.info("remove check : %s" % str(path))
            os.remove(path)
            restart = True

    # 5) restart service if changed
    logger.info("Restart Service ?? %s" % restart)
    if restart:
        p = Popen(["service", "consul", "restart"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        logger.info("%s" % out)

main()
