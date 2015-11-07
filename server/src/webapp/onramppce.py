"""Functionality to support interacting with an OnRamp PCE

Exports:
    PCEAccess: Client-side interface to OnRamp PCE server.
"""
import json
import os
import requests
import time

class PCEAccess():
    """Client-side interface to OnRamp PCE server.

    Methods:
        get_modules_avail: Return the list of modules that are available at the
            PCE but not currently installed.
        get_modules: Return the list of modules that are available at the PCE
            but not currently installed. (or a specific ID)
        add_module: Install given module on this PCE.
        deploy_module: Initiate module deployment actions.
        delete_module: Delete given module from PCE.
        get_jobs: Return the requested jobs.
        launch_job: Initiate job launch.
        delete_job: Delete given job from PCE.
        check_connection: Ping the server to see if it is still available.
        establish_connection: Handshake to establish authorization (JJH TODO).
    """
    _name = "[PCEAccess] "

    def __init__(self, logger, dbaccess, pce_id):
        """Initialize PCEAccess instance.

        Args:
            logger (logging.Logger): Logger for instance to use.
            dbaccess (onrampdb.DBAccess): Interface to server DB.
            pce_id (int): Id of PCE instance should provide interface to. Must
                exist in DB provided by dbaccess.
        """
        self._logger = logger
        self._db     = dbaccess
        self._pce_id = int(pce_id)

        #
        # Get the PCE server information
        #
        pce_info = self._db.pce_get_info(pce_id)
        self._url = "http://%s:%d" % (pce_info['data'][2], pce_info['data'][3])

    def _pce_get(self, endpoint, raw=False, **kwargs):
        """Execute GET request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
            raw (bool): If True, return raw response, else return JSON portion
                of response only.

        Kwargs:
            Key/val pairs in kwargs will become key/val pairs included as HTTP
            query paramaters in the request.

        Returns:
            JSON response object on success, 'None' on error.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        r = s.get(url, params=kwargs)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from GET %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return None
        else:
            if raw:
                return r
            return r.json()

    def _pce_post(self, endpoint, **kwargs):
        """Execute JSON-formatted POST request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
            raw (bool): If True, return raw response, else return JSON portion
                of response only.

        Kwargs:
            Key/val pairs in kwargs will be included as JSON key/val pairs in
            the request body.

        Returns:
            'True' if request was successfully processed by RXing PCE, 'False'
            if not.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        data = json.dumps(kwargs)
        headers = {"content-type": "application/json"}
        r = s.post(url, data=data, headers=headers)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from POST %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return False

        response = r.json()

        if ((not response) or ('status_code' not in response.keys())
            or (0 != response['status_code'])):
            return False

        return True

    def _pce_delete(self, endpoint):
        """Execute DELETE request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
        Returns:
            'True' if request was successfully processed by RXing PCE, 'False'
            if not.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        r = s.delete(url)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from DELETE %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return False
        else:
            response = r.json()
            if ((not response) or ('status_code' not in response.keys())
                or (0 != response['status_code'])):
                return False
            return True

    def get_modules_avail(self):
        """Return the list of modules that are available at the PCE but not
        currently installed.

        Returns:
            List of JSON-formatted module objects. Returns 'None' on error.
        """
        response = self._pce_get("modules", state="Available")
        if (not response) or ("modules" not in response.keys()):
            return None
        return [mod for mod in response["modules"]]

    def get_modules(self, id=None):
        """Return the requested modules.

        Args:
            id (int): Id of the requested module. 'None' to return all modules.

        Returns:
            JSON-formatted module object for given id, or if no id given, list
            of JSON-formatted module objects. Returns 'None' on error.
        """
        url = "modules"
        if id:
            url += "/%d" % id

        response = self._pce_get(url)
        if not response:
            return None

        if id:
            if "module" not in response.keys():
                return None
            return response["module"]

        if "modules" not in response.keys():
            return None
        return [mod for mod in response["modules"]]
            

    def add_module(self, id, module_name, mod_type, mod_path):
        """Install given module on this PCE.

        Args:
            id (int): Id to be given to installed module on PCE.
            module_name (str): Name to be given to installed module on PCE.
            mod_type (str): Type of module source. Currently supported options:
                'local'.
            mod_path (str): Path, formatted as required by given mod_type, of
                the installation source.

        Returns:
            'True' if installation request was successfully processed, 'False'
            if not.
        """
        payload = {
            'mod_id': id,
            'mod_name': module_name,
            'source_location': {
                'type': mod_type,
                'path': mod_path
            }
        }
        return self._pce_post("modules", **payload)

    def deploy_module(self, id):
        """Initiate module deployment actions.

        Args:
            id (int): Id of the installed module to deploy.

        Returns:
            'True' if deployment request was successfully processed, 'False'
            if not.
        """
        endpoint = "modules/%d" % id
        return self._pce_post(endpoint)

    def delete_module(self, id):
        """Delete given module from PCE.

        Args:
            id (int): Id of the module to delete.

        Returns:
            'True' if delete request was successfully processed, 'False'
            if not.
        """
        endpoint = "modules/%d" % id
        return self._pce_delete(endpoint)

    def get_jobs(self, id):
        """Return the requested jobs.

        Args:
            id (int): Id of the requested job. 'None' to return all jobs.

        Returns:
            JSON-formatted job object for given id, or if no id given, list
            of JSON-formatted job objects. Returns 'None' on error.
        """
        url = "jobs/%d" % id

        response = self._pce_get(url)

        if not response:
            return None
        if "job" not in response.keys():
            return None

        return response["job"]


    def launch_job(self, user, mod_id, job_id, run_name, cfg_params=None):
        """Initiate job launch.

        Args:
            user (str): Username of user launching job.
            mod_id (int): Id of the module to run.
            job_id (int): Id to be given to launched job on PCE.
            run_name (str): Human-readable identifier for job.
            cfg_params (dict): Dict containing attrs to be written to
                onramp_runparams.cfg

        Returns:
            'True' if launch request was successfully processed, 'False' if not.
        """
        payload = {
            'username': user,
            'mod_id': mod_id,
            'job_id': job_id,
            'run_name': run_name
        }
        if cfg_params:
            payload['cfg_params'] = cfg_params
        return self._pce_post("jobs", **payload)

    def delete_job(self, id):
        """Delete given job from PCE.

        Args:
            id (int): Id of the job to delete.

        Returns:
            'True' if delete request was successfully processed, 'False'
            if not.
        """
        endpoint = "jobs/%d" % id
        return self._pce_delete(endpoint)

    def ping(self):
        """Ping the given PCE.

        Returns:
            HTTP response code from PCE ping request.
        """
        endpoint = "cluster/ping"
        return self._pce_get(endpoint, raw=True).status_code

    def check_connection(self):
        """Ping the server to see if it still available. Record status in given
        DB.

        Returns:
            True if connected, False if not.
        """
        status_code = self.ping()

        self._logger.debug("%scheck_connection() %d from %s"
                           % (self._name, status_code, self._url))

        if status_code == 200:
            self._db.pce_update_state( self._pce_id, 0 ) # see onrampdb.py
            return True
        else:
            self._db.pce_update_state( self._pce_id, 2 ) # see onrampdb.py
            return False

    def establish_connection(self):
        #
        # Handshake to establish authorization (JJH TODO)
        #
        self._logger.debug(self._name + "establish_connection() Authorize - TODO")

        #
        # Check if it is a valid connection
        #
        is_connected = self.check_connection()
        if is_connected is False:
            return False

        #
        # Access the list of available modules
        #
        return self._refresh_modules_in_db( ("%sestablish_connection()" % self._name), avail=True )


    def refresh_module_states(self, module_id=None):
        if module_id is None:
            prefix = ("%srefresh_module_states()" % self._name)
        else:
            prefix = ("%srefresh_module_states(%s)" % (self._name, str(module_id)))

        self._refresh_modules_in_db(prefix, module_id)

    def _refresh_modules_in_db(self, prefix, module_id=None, avail=False):
        if module_id is None:
            if avail is True:
                self._logger.debug("%s Get all available modules" % prefix)
                avail_mods = self.get_modules_avail()
            else:
                self._logger.debug("%s Get all modules" % prefix)
                avail_mods = self.get_modules()
        else:
            self._logger.debug("%s Get module info for %s" % (prefix, str(module_id)))
            # JJH the below does not work as expected, so intead grab the whole
            #     list and extract just the one we care about
            #avail_mods = self.get_modules( int(module_id) )
            module_id = int(module_id)
            all_mods = self.get_modules()
            avail_mods = None
            for m in all_mods:
                m_id = self._db.module_lookup(m['mod_name'])
                if m_id == module_id:
                    avail_mods = m
                    self._logger.debug("%s Get module info for %s: Found (I)" % (prefix, str(module_id)))
                    break

            if avail_mods is None:
                self._logger.debug("%s Get module info for %s: Searching Available" % (prefix, str(module_id)))
                all_mods = self.get_modules_avail()
                avail_mods = None
                for m in all_mods:
                    m_id = self._db.module_lookup(m['mod_name'])
                    if m_id == module_id:
                        avail_mods = m
                        self._logger.debug("%s Get module info for %s: Found (A)" % (prefix, str(module_id)))
                        break


        if avail_mods is None:
            self._db.pce_update_state( self._pce_id, 2 ) # see onrampdb.py
            return False


        if module_id is None:
            for module in avail_mods:
                rtn = self._update_module_in_db(prefix, module)
                if rtn is False:
                    return False
        else:
            return self._update_module_in_db(prefix, avail_mods)

        return True

    def _update_module_in_db(self, prefix, module):
        if module['state'] == "Does not exist":
            self._logger.error("%s Asking to update a module that does not exist. %s" % (prefix, str(module)))
            self._db.pce_update_module_state(self._pce_id, module["mod_id"], 0) # see onrampdb.py
            return False

        self._logger.debug("%s Add Module: %s" % (prefix, module['mod_name']))
        mod_info = self._db.module_add_if_new(module['mod_name'])
        module_id = int(mod_info['id'])

        # Add it to the PCE/Module pair table (if not already there)
        self._logger.debug("%s Add Module to PCE: %d module %d" 
                           % (prefix, self._pce_id, module_id))

        pair_info = self._db.pce_add_module(self._pce_id, module_id,
                                            module['source_location']['type'],
                                            module['source_location']['path'])

        self._logger.debug("%s Add Module to PCE: %d module %d : State = %s" 
                           % (prefix, self._pce_id, module_id, str(module['state'])))
        state = -1
        if module['state'] == "Does not exist":
            state =  0
        elif module['state'] == "Available":
            state =  1
        elif module['state'] == "Checkout in progress":
            state =  2
        elif module['state'] == "Checkout failed":
            state = -2
        elif module['state'] == "Installed":
            state =  3
        elif module['state'] == "Deploy in progress":
            state =  4
        elif module['state'] == "Deploy failed":
            state = -4
        elif module['state'] == "Admin required":
            state =  5
        elif module['state'] == "Module ready":
            state =  6

        self._db.pce_update_module_state(self._pce_id, module_id, state) # see onrampdb.py


    def install_and_deploy_module(self, module_id):
        prefix = ("%sinstall_deploy()" % self._name)

        #
        # Make sure this ID is available on the PCE
        #
        if self._refresh_modules_in_db( prefix ) is False:
            return {'error_msg' : "Module with id %d does not exist on the PCE" % (module_id)}

        # Get module info from db
        rtn = self._db.pce_get_modules(self._pce_id, module_id)
        # Convert to dictionary for ease of use
        module_info = dict( zip( rtn["fields"], rtn["data"] ) )
        self._logger.debug("%s Module state %d (%s)" % (prefix, module_info["state"], module_info["state_str"]))

        #
        # Install the module (if it is not already installed)
        #
        if module_info["state"] <= 1:
            rtn = self.add_module( module_info["module_id"], module_info["module_name"], module_info["src_location_type"], module_info["src_location_path"] )
            if rtn is False:
                return {'error_msg' : "Failed to install the module"}
            self._logger.debug("%s Module %d installed" % (prefix, module_id) )
        else:
            self._logger.debug("%s Module %d already installed (state=%d)" % (prefix, module_id, module_info["state"]) )

        #
        # Deploy the module (if it is not already deployed successfully)
        #
        if module_info["state"] not in [4, 5, 6]:
            rtn = self.deploy_module(int(module_id))
            if rtn is False:
                return {'error_msg' : "Failed to deploy the module"}
            self._logger.debug("%s Module %d deployed" % (prefix, module_id) )
        else:
            self._logger.debug("%s Module %d already deploy(ing) (state=%d)" % (prefix, module_id, module_info["state"]) )

        #
        # Update the DB
        #
        self._refresh_modules_in_db( prefix, module_id )
        #self._refresh_modules_in_db( prefix )

        # rdata = self._db.pce_add_module( pce_id, module_id )
        # if 'error_msg' in rdata.keys():
        #     self.logger.info(prefix + " " + rdata['error_msg'])
        #     raise cherrypy.HTTPError(400)

        return {}

if __name__ == '__main__':

    import logging
    import sys
    import time

    if len(sys.argv) < 3:
        sys.exit('usage: python onramppce.py IP_ADDRESS PORT')
    class Dummy:
        _ip_addr = sys.argv[1]
        _port = int(sys.argv[2])
        def __init__(self, logger):
            self.logger = logger

        def pce_get_info(self, pce_id):
            return {'data': (None, None, self._ip_addr, self._port)}

        def pce_add_module(self, *args):
            self.logger.debug('pce_add_module: pce_id %d, mod_id %d, '
                              'source_type %s, path %s' % args)
            return None

        def pce_update_module_state(self, *args):
            self.logger.debug('pce_update_module_state: pce_id %d, mod_id %d, '
                              'state %d' % args)

        def pce_update_state(self, *args):
            self.logger.debug('pce_update_state: pce_id %d, state %d' % args)

        def module_add_if_new(self, *args):
            self.logger.debug('module_add_if_new: mod_name %s' % args)
            return {'exits':True, 'id':1}

    log_name = 'onramp'
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('test.log')
    handler.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s %(message)s'))
    logger.addHandler(handler)

    pce = PCEAccess(logger, Dummy(logger), 1)
    print 'Connection'
    print pce.establish_connection()
    print 'Available mods'
    avail_mods = pce.get_modules_avail()
    print avail_mods
    print 'Mods before install'
    print pce.get_modules()
    print 'Installing all available mods...'
    i = 1
    for mod in avail_mods:
        source = mod['source_location']
        pce.add_module(i, 'test%d' % i, source['type'], source['path'])
        i += 1
    time.sleep(5)
    print 'Mods after install'
    installed_mods = pce.get_modules()
    print installed_mods
    print 'Deploying all installed mods...'
    for mod in installed_mods:
        pce.deploy_module(mod['mod_id'])
    time.sleep(5)
    print 'Mods after deploy'
    deployed_mods = pce.get_modules()
    print deployed_mods
    print 'Deleting "Admin required" modules...'
    for mod in deployed_mods:
        if mod['state'] == 'Admin required':
            pce.delete_module(mod['mod_id'])
    time.sleep(5)
    print 'Mods after delete'
    ready_mods = pce.get_modules()
    print ready_mods
    print 'Individual module'
    print pce.get_modules(1)
    print 'Launching jobs...'
    job_attrs = {
        'onramp': {'np': 2, 'nodes': 1},
        'ring': {'iters': 1, 'work': 1},
        'hello': {'name': 'testname'}
    }
    i = 1
    for mod in ready_mods:
        pce.launch_job('testuser', mod['mod_id'], i, 'run%d' % i,
                       cfg_params=job_attrs)
        i += 1
    print 'Launched jobs'
    jobs = map(pce.get_jobs, range(1, i))
    print jobs
    print 'Pausing to let jobs finish...'
    time.sleep(5)
    print 'Postprocessing jobs'
    jobs = map(pce.get_jobs, range(1, i))
    print jobs
    print 'Pausing to let jobs finish postprocessing...'
    time.sleep(5)
    print 'Done jobs'
    jobs = map(pce.get_jobs, range(1, i))
    print jobs
    print 'Deleting jobs'
    jobs = map(pce.delete_job, range(1, i))
    jobs = map(pce.get_jobs, range(1, i))
    print 'Remaining jobs (each job should be empty)'
    print jobs
