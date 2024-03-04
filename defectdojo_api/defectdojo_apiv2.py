import json
import requests
import requests.exceptions
import urllib3
import datetime

urllib3.add_stderr_logger()

version = "1.1.6.dev2"

class DefectDojoAPIv2(object):
    """An API wrapper for DefectDojo."""

    def __init__(self, host, api_token, user, api_version='v2', verify_ssl=True, timeout=4000, proxies=None, user_agent=None, cert=None, debug=False):
        """Initialize a DefectDojo API instance.

        :param host: The URL for the DefectDojo server. (e.g., http://localhost:8000/DefectDojo/)
        :param api_token: The API token generated on the DefectDojo API key page.
        :param user: The user associated with the API key.
        :param api_version: API version to call, the default is v1.
        :param verify_ssl: Specify if API requests will verify the host's SSL certificate, defaults to true.
        :param timeout: HTTP timeout in seconds, default is 30.
        :param proxis: Proxy for API requests.
        :param user_agent: HTTP user agent string, default is "DefectDojo_api/[version]".
        :param cert: You can also specify a local cert to use as client side certificate, as a single file (containing
        the private key and the certificate) or as a tuple of both file's path
        :param debug: Prints requests and responses, useful for debugging.

        """

        self.host = str(host) + '/api/' + str(api_version) + '/'
        self.api_token = api_token
        self.user = user
        self.api_version = api_version
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self.timeout = timeout

        if not user_agent:
            self.user_agent = 'DefectDojo_api/' + version
        else:
            self.user_agent = user_agent

        self.cert = cert
        self.debug = debug  # Prints request and response information.

        if not self.verify_ssl:
            urllib3.disable_warnings()  # Disabling SSL warning messages if verification is disabled.

    def version_url(self):
        """Returns the DefectDojo API version.

        """
        return self.api_version

    def get_id_from_url(self, url):
        """Returns the ID from the DefectDojo API.

        :param url: URL returned by the API

        """
        url = url.split('/')
        return url[len(url)-2]
    ###### Global Roles#######
    def get_roles(self, limit=20000):
        """Retrieves all dojo_roles like Maintainer, Owner"""
        params  = {}
        if limit:
            params['limit'] = limit
        return self._request('GET', 'roles/', params)

    def get_global_roles(self, limit=20000):
        """Retrieves all dojo_global_roles"""
        params  = {}
        if limit:
            params['limit'] = limit
        return self._request('GET', 'global_roles/', params)    
    
    def post_user_global_role(self, user_id, group=None, role=None):
        """ adds a user to a global role"""
        data = {}
        data['user'] = user_id
        if group:
            data['group'] = group
        else:
            data['group'] = None #can specify the product group here, irritating because of product_role call
        data['role'] = role
        return self._request('POST', 'global_roles/', data=data)

    def patch_user_global_role(self, id, user_id, group=None, role=None):
        """ adds a user to a global role"""
        data = {}
        data['user'] = user_id
        data['group'] = group #can specify the product group here, irritating because of product_role call
        data['role'] = role
        return self._request('PATCH', 'global_roles/'+ str(id) + '/', data=data)

    ###### Dojo Group API and Dojo Group Member API and Product Group API#######
    def list_dojo_groups(self, limit=20000):
        """Retrieves all dojo_groups"""
        params  = {}
        if limit:
            params['limit'] = limit
        return self._request('GET', 'dojo_groups/', params)
    
    def list_dojo_group_members(self, id=None, group_id=None):
        """Retrieves all dojo_groups"""
        params  = {}
        if group_id != None:
            params["group_id"]=group_id

        if id != None:
            return self._request('GET', 'dojo_group_members/'+ str(id) + '/', params=params)
        else: 
            return self._request('GET', 'dojo_group_members/',params=params)

    def create_dojo_group(self,name,description=None,social_provider=None):
        data={}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if social_provider:
            data['social_provider'] = social_provider
        return self._request('POST','dojo_groups/',data=data)

    def post_dojo_group_members(self,group,user,role):
        """POST group members"""
        data={}
        data['group'] = group
        data['user'] = user
        data['role'] = role
        return self._request('POST','dojo_group_members/',data=data)

    def put_dojo_group_members(self,id,group,user,role):
        """PUT group members"""
        data={}
        data['group'] = group
        data['user'] = user
        data['role'] = role
        return self._request('PUT','dojo_group_members/'+ str(id) + '/',data=data)

    def delete_dojo_group_members(self,id):
        """Delete group members"""
        return self._request('DELETE','dojo_group_members/'+ str(id) + '/')

    def post_product_group(self,product,group,role):
        """POST group members"""
        data={}
        data['product'] = product
        data['group'] = group
        data['role'] = role
        return self._request('POST','product_groups/',data=data)

    def delete_product_group(self,group):
        """Delete group members"""
        return self._request('DELETE', 'product_groups/' + str(group) + '/')

    def get_dojo_product_group_member(self, product_id, limit=20000):
        """Retrieves all member of dojo_product_groups"""
        params  = {}
        if limit:
            params['limit'] = limit
        params['product_id'] = product_id
        return self._request('GET', 'product_groups/', params)

    ###### User API #######
    def list_users(self, username=None, email=None,limit=20000):
        """Retrieves all the users.

        :param username: Search by username.
        :param limit: Number of records to return.

        """
        params  = {}
        if limit:
            params['limit'] = limit

        if username:
            params['username'] = username
        if email:
            params['email'] = email

        return self._request('GET', 'users/', params)

    def list_users_names(self):
        """ list all user names """
        out=self.list_users().data['results']
        output=[]
        for iterator in out:
            output.append(iterator['username'])
        return output
    
    def list_users_emails(self):
        """ list all users email """
        out = self.list_users().data['results']
        output = []
        for iterator in out:
            output.append(iterator['email'])
        return output

    def get_user_id_by_name(self, user_name):
        """Retrieves a user using the given user name."""
        req=self.list_users(username=user_name).data['results']
        output=None
        for iterate in req:
            if str(user_name)==iterate['username']:
                output=iterate['id']
        return output

    def get_user_by_name(self, user_name):
        """Retrieves a user using the given user name."""

        req = self.list_users(username=user_name).data['results']
        for iterate in req:
            if user_name == iterate['username']:
                output = self.get_user_by_id(iterate['id'])
        return output
    
    def get_user_by_email(self, email):
        """Retrieve user by given email
        :param email: User email
        """
        output=self._request('GET', '/users',params={'email':email}).data['results']
        if len(output) > 0:
            return output[0]
        else:
            return None
    
    def get_user_id_by_email(self, email):
        req = self.list_users(email=email).data['results']
        output = None
        for iterate in req:
            if str(email) == iterate['email']:
                output = iterate['id']
        return output
        
    def get_user_by_id(self, user_id):
        """Retrieves a user using the given user id.

        :param user_id: User identification.

        """
        return self._request('GET', 'users/' + str(user_id) + '/')

    def patch_user(self, user_id, is_active = None, is_superuser = None, password = None, email = None, first_name = None, last_name = None, username = None):
        """Retrieves a user using the given user id.

        :param user_id: User identification.

        """
        data = {}

        if username:
            data['username'] = username

        if is_active:
            data['is_active'] = is_active

        if is_superuser:
            data['is_superuser'] = is_superuser

        if password:
            data["password"] = password
        
        if first_name:
            data["first_name"] = first_name

        if last_name:
            data["last_name"] = last_name

        if email:
            data["email"] = email

        return self._request('PATCH', 'users/' + str(user_id) + '/', data=data)

    def delete_user(self, user_id):
        """Delete a user using the given user id.
        Args:
            user_id (int): A unique integer value identifying ths user.
        """
        return self._request('DELETE', f'users/{user_id}/')

    def create_user(self,user_name,first_name=None,last_name=None,email=None,is_active=True,is_superuser=False, password="asdf"): # nosec
        """password have to change this is justfor development use only"""
        data={"username":user_name,
              "is_active":is_active,
              "password":password}
        if first_name:
            data['first_name'] = first_name
        if last_name:
            data['last_name'] = last_name
        if email:
            data['email'] = email
        if is_superuser:
            data['is_superuser'] = is_superuser
        return self._request('POST','users/',data=data)

    def delete_preview_user(self,user_id,limit=2000):
        """checks if a user can be safely deleted"""
        params = {}
        if limit:
            params['limit'] = limit
        
        return self._request('GET',f'users/{user_id}/delete_preview/', params).data['results']
    
    ###### User contact info API #######

    def list_user_contact_info(self, user_id=None, slack_username=None, block_execution=None, cell_number=None, github_username=None, offset=None, prefetch=None, slack_user_id=None, title=None, twitter_username=None, limit=20000):
        """Retrieves the user contact info"""

        params  = {}
        if limit:
            params['limit'] = limit

        if user_id:
            params['user'] = user_id
        if slack_username:
            params['slack_username'] = slack_username
        if block_execution:
            params['block_execution'] = block_execution
        if cell_number:
            params['cell_number'] = cell_number
        if github_username:
            params['github_username'] = github_username
        if offset:
            params['offset'] = offset
        if prefetch:
            params['prefetch'] = prefetch
        if slack_user_id:
            params['slack_user_id'] = slack_user_id
        if title:
            params['title'] = title
        if twitter_username:
            params['twitter_username'] = twitter_username

        return self._request('GET', 'user_contact_infos/', params)
    
    def get_user_contact_info(self, id, slack_username=None, block_execution=None, cell_number=None, github_username=None, offset=None, prefetch=None, slack_user_id=None, title=None, twitter_username=None, limit=20000):
        """Retrieves the user contact info"""
        return self._request('GET', 'user_contact_infos/'+ str(id) + '/')

    def patch_user_contact_info(self, user_id, title=None, phone_number=None, cell_number=None, twitter_username=None, github_username=None, slack_username=None, slack_user_id=None, block_execution=None, force_password_reset=None):
        """Patches a users contact info

        :param user_id: User identification.

        """
        data = {}

        if title:
            data['title'] = title
        if phone_number:
            data['phone_number'] = phone_number
        if cell_number:
            data['cell_number'] = cell_number
        if twitter_username:
            data["twitter_username"] = twitter_username
        if github_username:
            data["github_username"] = github_username
        if slack_username:
            data["slack_username"] = slack_username
        if slack_user_id:
            data["slack_user_id"] = slack_user_id
        if block_execution:
            data["block_execution"] = block_execution
        if force_password_reset:
            data["force_password_reset"] = force_password_reset
        
        data["user"] = user_id

        return self._request('PATCH', 'user_contact_infos/' + str(user_id) + '/', data=data)
        
    def post_user_contact_info(self, user_id, title=None, phone_number=None, cell_number=None, twitter_username=None, github_username=None, slack_username=None, slack_user_id=None, block_execution=None, force_password_reset=None):
        """Sets a users contact info

        :param user_id: User identification.

        """
        data = {}

        if title:
            data['title'] = title
        if phone_number:
            data['phone_number'] = phone_number
        if cell_number:
            data['cell_number'] = cell_number
        if twitter_username:
            data["twitter_username"] = twitter_username
        if github_username:
            data["github_username"] = github_username
        if slack_username:
            data["slack_username"] = slack_username
        if slack_user_id:
            data["slack_user_id"] = slack_user_id
        if block_execution:
            data["block_execution"] = block_execution
        if force_password_reset:
            data["force_password_reset"] = force_password_reset
        
        data["user"] = user_id

        return self._request('POST', 'user_contact_infos/', data=data)

    ###### Engagements API #######
    def list_engagements(self, status=None, product_id=None, limit=20000):
        """Retrieves all the engagements.

        :param product_in: List of product ids (1,2).
        :param name_contains: Engagement name
        :param limit: Number of records to return.

        """

        params = {}
        if limit:
            params['limit'] = limit

        if product_id:
            params['product'] = product_id

        if status:
            params['status'] = status

        return self._request('GET', 'engagements/', params)

    def list_engagement_ids_name_contains(self, name_contains=None, limit=20000):
        """Retrieves all the engagements.

        :param product_in: List of product ids (1,2).
        :param name_contains: Engagement name
        :param limit: Number of records to return.

        """

        params = {}
        if limit:
            params['limit'] = limit

        if name_contains:
            out=self._request('GET', 'engagements/', params)
            engagement=out.data['results']
            name_list=list()
            import re
            for engage in engagement:
                if re.search(name_contains.lower(),engage['name'].lower()):
                    name_list.append(engage['id'])
        return name_list

    def get_engagement_by_id(self, engagement_id):
        """Retrieves an engagement using the given engagement id.

        :param engagement_id: Engagement identification.

        """
        return self._request('GET', 'engagements/' + str(engagement_id) + '/')

    def get_engagement_id_by_name(self, engagement_name, product_name = None, exact_product_name=None):
        if exact_product_name != None:
            product_id = self.get_product_id_by_exact_name(product_name=exact_product_name)
        else:
            product_id = self.get_product_id_by_name(product_name=product_name)
        result = [ engagement for engagement in self.list_engagements(limit=20000).data['results'] if engagement['product'] == product_id and engagement['active'] != False and engagement['name'] == engagement_name ]
        return result[0]['id'] if len(result) == 1 else False

    def post_engagement_report(self,engagement_id, fulldata=False, include_executive_summary=False):
        data = {}
        if include_executive_summary == False:
            data['include_executive_summary'] = False
        else:
            data['include_executive_summary'] = True
        if fulldata == False:
            data['include_finding_notes'] = False
            data['include_finding_images'] = False
            data['include_table_of_contents'] = False
            return self._request('POST','engagements/'+ str(engagement_id) + '/generate_report/', data=data)
        else:
            self._request('POST','engagements/'+ str(engagement_id) + '/generate_report/')

    def list_engagement_ids_by_product_id(self, product_id):
        req=self.list_engagements(limit=20000).data['results']
        engagement_list=[]
        for iterator in req:
            if str(iterator['product'])==str(product_id) and str(iterator['active']) != 'False':
                appendant=iterator['id']
                engagement_list.append(appendant)
        return engagement_list

    def list_engagement_ids_by_product_name(self, name):
        req=self.list_engagements(limit=20000).data['results']
        product_id=self.get_product_id_by_name(name)
        engagement_list=[]
        for iterator in req:
            if str(iterator['product'])==str(product_id) and str(iterator['active']) != 'False':
                appendant = iterator['id']
                engagement_list.append(appendant)
        return engagement_list

    def list_engagement_names_by_product_name(self, name):
        req=self.list_engagements(limit=20000).data['results']
        product_id=self.get_product_id_by_name(name)
        engagement_list=[]
        for iterator in req:
            if str(iterator['product'])==str(product_id) and str(iterator['active']) != 'False':
                appendant = iterator['name']
                engagement_list.append(appendant)
        return engagement_list

    def create_engagement(self, name, product_id, lead_id, status, target_start, target_end, active='True',
        pen_test='False', check_list='False', threat_model='False', risk_path="",test_strategy="", progress="",
        done_testing='False', engagement_type="CI/CD", build_id=None, commit_hash=None, branch_tag=None, build_server=None,
        source_code_management_server=None, source_code_management_uri=None, orchestration_engine=None, description=None, deduplication_on_engagement=True):
        """Creates an engagement with the given properties.

        :param name: Engagement name.
        :param product_id: Product key id..
        :param lead_id: Testing lead from the user table.
        :param status: Engagement Status: In Progress, On Hold, Completed.
        :param target_start: Engagement start date.
        :param target_end: Engagement end date.
        :param active: Active
        :param pen_test: Pen test for engagement.
        :param check_list: Check list for engagement.
        :param threat_model: Thread Model for engagement.
        :param risk_path: risk_path
        :param test_strategy: Test Strategy URLs
        :param progress: Engagement progresss measured in percent.
        :param engagement_type: Interactive or CI/CD
        :param build_id: Build id from the build server
        :param commit_hash: Commit hash from source code management
        :param branch_tag: Branch or tag from source code management
        :param build_server: Tool Configuration id of build server
        :param source_code_management_server: URL of source code management
        :param source_code_management_uri: Link to source code commit
        :param orchestration_engine: URL of orchestration engine
        :param deduplication_on_engagement: boolean value for deduplication_on_engagement

        """

        data = {
            'name': name,
            'product': product_id,
            'lead': lead_id,
            'status': status,
            'target_start': target_start,
            'target_end': target_end,
            'active': active,
            'pen_test': pen_test,
            'check_list': check_list,
            'threat_model': threat_model,
            'risk_path': risk_path,
            'test_strategy': test_strategy,
            'progress': progress,
            'done_testing': done_testing,
            'engagement_type': engagement_type
        }

        if description:
            data.update({'description': description})

        if build_id:
            data.update({'build_id': build_id})

        if commit_hash:
            data.update({'commit_hash': commit_hash})

        if branch_tag:
            data.update({'branch_tag': branch_tag})

        if build_server:
            data.update({'build_server': build_server})

        if source_code_management_server:
            data.update({'source_code_management_server': source_code_management_server})

        if source_code_management_uri:
            data.update({'source_code_management_uri': source_code_management_uri})

        if orchestration_engine:
            data.update({'orchestration_engine': orchestration_engine})

        if deduplication_on_engagement:
            data.update({'deduplication_on_engagement': deduplication_on_engagement})

        return self._request('POST', 'engagements/', data=data)

    def close_engagement(self, id, user_id=None):

        """Closes an engagement with the given properties.
        :param id: Engagement id.
        :param user_id: User from the user table.
        """

        return self._request('POST', 'engagements/{id}/close')

    def set_engagement(self, id, product_id=None, lead_id=None, name=None, status=None, target_start=None,
        target_end=None, active=None, pen_test=None, check_list=None, threat_model=None, risk_path=None,
        test_strategy=None, progress=None, done_testing=None, engagement_type="CI/CD", build_id=None, commit_hash=None, branch_tag=None, build_server=None,
        source_code_management_server=None, source_code_management_uri=None, orchestration_engine=None, description=None):

        """Updates an engagement with the given properties.

        :param id: Engagement id.
        :param name: Engagement name.
        :param product_id: Product key id..
        :param lead_id: Testing lead from the user table.
        :param status: Engagement Status: In Progress, On Hold, Completed.
        :param target_start: Engagement start date.
        :param target_end: Engagement end date.
        :param active: Active
        :param pen_test: Pen test for engagement.
        :param check_list: Check list for engagement.
        :param threat_model: Thread Model for engagement.
        :param risk_path: risk_path
        :param test_strategy: Test Strategy URLs
        :param progress: Engagement progresss measured in percent.
        :param engagement_type: Interactive or CI/CD
        :param build_id: Build id from the build server
        :param commit_hash: Commit hash from source code management
        :param branch_tag: Branch or tag from source code management
        :param build_server: Tool Configuration id of build server
        :param source_code_management_server: URL of source code management
        :param source_code_management_uri: Link to source code commit
        :param orchestration_engine: URL of orchestration engine
        """

        data = {}

        if name:
            data['name'] = name

        if product_id:
            data['product'] = product_id

        if lead_id:
            data['lead'] = lead_id

        if status:
            data['status'] = status

        if target_start:
            data['target_start'] = target_start

        if target_end:
            data['target_end'] = target_end

        if active is not None:
            data['active'] = active

        if pen_test:
            data['pen_test'] = pen_test

        if check_list:
            data['check_list'] = check_list

        if threat_model:
            data['threat_model'] = threat_model

        if risk_path:
            data['risk_path'] = risk_path

        if test_strategy:
            data['test_strategy'] = test_strategy

        if progress:
            data['progress'] = progress

        if done_testing:
            data['done_testing'] = done_testing

        if engagement_type:
            data['engagement_type'] = engagement_type

        if description:
            data['description'] = description
        
        if source_code_management_uri:
            data['source_code_management_uri'] = source_code_management_uri
        
        if branch_tag:
            data['branch_tag'] = branch_tag

        return self._request('PATCH', 'engagements/' + str(id) + '/', data=data)
    
    def delete_engagement(self,engagement_id):
        """ Delete engagement using engagement id
        """
        return self._request('DELETE', 'engagements/' + str(engagement_id) + '/')

   ###### Product_Types API #######

    def get_product_types(self):
        """Returns the DefectDojo API URI for the product_types.
            Output is a List of all product_types
        """
        request=self._request('GET', 'product_types/',).data["results"]
        output=[]
        for iterator in request:
            cache={str(iterator["name"])} #TODO make a dictionary
            output.append(cache)
        return output

    def get_product_types_id_and_name(self):
        request=self._request('GET', 'product_types/',).data["results"]
        return request

    def get_product_type_id_by_name(self, name):
        """Returns the DefectDojo API URI for the product_types.
                    Output is the id of the product_type
                """
        request = self._request('GET', 'product_types/', ).data["results"]
        output = []
        for iterator in request:
            if str(iterator["name"]) == name:
                output = str(iterator["id"])
        return output

    def create_product_type(self, product_type_name):
        """Creates a product_type"""

        data = {
            'name': product_type_name
        }
        return self._request('POST', 'product_types/', data=data)

    def delete_product_type(self, product_type_id):
        """Delete a product_type"""

        return self._request('DELETE', 'product_types/' + str(product_type_id) + '/')

    ###### Product API #######
    def list_products(self, name=None, name_contains=None, limit=20000,name_exact=None):
        """Retrieves all the products.

        :param name: Search by product name.
        :param name_contains: Search by product name.
        :param limit: Number of records to return.
        :param name_exact: exact product name to search.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if name:
            params['name'] = name

        if name_contains:
            params['name__icontains'] = name_contains
        
        if name_exact:
            params['name_exact'] = name_exact
            
        return self._request('GET', 'products/', params)

    def get_products_names(self):
        """ Get a List of all Product_names"""
        product_names_list=[]
        output=self.list_products().data["results"]
        for iterator in output:
            product_names_list.append(iterator["name"])
        return product_names_list

    def get_product_id_by_name(self, product_name):
        try:
            product_id = self.list_products(name=product_name).data['results'][0]['id']
        except (NameError, IndexError):
            product_id=False
        return product_id
    
    def get_product_id_by_exact_name(self, product_name):
        try:
            product_id = self.list_products(name_exact=product_name).data['results'][0]['id']
        except (NameError, IndexError):
            product_id=False
        return product_id

    def get_product_description_by_name(self, product_name):
        output=self.get_product_by_name(product_name)
        return output.data["description"]

    def get_product_type_by_name(self, product_name):
        output=self.get_product_by_name(product_name)
        return output.data["prod_type"]

    def get_product_by_name(self, product_name):
        output = self.list_products().data["results"]

        for iterator in output:
            if iterator["name"] == product_name:
                product_id=iterator["id"]
        try:
            product=self.get_product_by_id(product_id)
        except:
            product=False
        return product

    def get_product_by_id(self, product_id):
        """Retrieves a product using the given product id.

        :param product_id: Product identification.

        """
        return self._request('GET', 'products/' + str(product_id) + '/')

    def create_product(self, name, description, prod_type, tags = None):
        """Creates a product with the given properties.

        :param name: Product name.
        :param description: Product key id..
        :param prod_type: Product type.

        """

        data = {
            'name': name,
            'description': description,
            'prod_type': prod_type
        }

        if tags:
            data['tags'] = tags

        return self._request('POST', 'products/', data=data)

    def delete_product(self, product_id):
        """Deletes a product using the given product id.

        :param product_id: Product identification.

        """
        return self._request('DELETE', 'products/' + str(product_id) + '/')

    def set_product(self, product_id, name=None, description=None, prod_type=None, tags=None):
        """Updates a product with the given properties.

        :param product_id: Product ID
        :param name: Product name.
        :param description: Product key id..
        :param prod_type: Product type.

        """
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if prod_type:
            data['prod_type'] = prod_type

        if tags:
            data['tags'] = tags

        return self._request('PUT', 'products/' + str(product_id) + '/', data=data)

    def patch_product(self, product_id, name=None, description=None, prod_type=None, authorized_users=None, enable_simple_risk_acceptance=None):
        """Updates a product with the given properties.

        :param product_id: Product ID
        :param name: Product name.
        :param description: Product key id..
        :param prod_type: Product type.

        """

        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if prod_type:
            data['prod_type'] = prod_type

        if authorized_users: #TODO Test
            data['authorized_users'] = authorized_users

        if enable_simple_risk_acceptance:
            data['enable_simple_risk_acceptance'] = enable_simple_risk_acceptance

        return self._request('PATCH', 'products/' + str(product_id) + '/', data=data)

    def post_product_report(self,product_id, fulldata=False):
        if fulldata == False:
            data = {}
            data['include_finding_notes'] = False
            data['include_finding_images'] = False
            data['include_executive_summary'] = False
            data['include_table_of_contents'] = False
            return self._request('POST','products/'+ str(product_id) + '/generate_report/', data=data)
        else:
            return self._request('POST','products/'+ str(product_id) + '/generate_report/')
        
    def set_product_api_scan_configuration(self, product_id, tool_configuration, service_key_1 = None, service_key_2 = None, service_key_3 = None):
        """Updates a product with the given properties

        """
        data = {}

        data['product'] = product_id
        data['tool_configuration'] = int(tool_configuration)

        if service_key_1:
            data['service_key_1'] = service_key_1

        if service_key_2:
            data['service_key_2'] = service_key_2

        if service_key_3:
            data['service_key_3'] = service_key_3

        return self._request('POST', 'product_api_scan_configurations/', data=data)

    def get_product_api_scan_configuration(self, product_id, service_key_1 = None, service_key_2 = None):
        """
        """
        data = {}

        if service_key_1:
            data['service_key_1'] = service_key_1
        if service_key_2:
            data['service_key_2'] = service_key_2
        
        return self._request('GET', f'product_api_scan_configurations/?product={product_id}', data=data)
    
    def get_tool_types(self):
        """

        Receives Tool type configurations

        """

        return self._request('GET', 'tool_types/')
    
    def get_tool_types_by_id(self,id):
        """

        Receives Tool type configurations

        """

        return self._request('GET', f'tool_types/{id}/').data['results']
    
    def get_tool_configurations(self, tool_type = None):
        """

        Receives Tool type configurations

        """
        data = {}

        if tool_type:
            data['tool_type'] = tool_type

        return self._request('GET', f'tool_configurations/', data=data).data['results']
    
    def get_tool_configurations_by_id(self,id):
        """

        Receives specific Tool type configurations

        """

        return self._request('GET', f'tool_configurations/{id}/').data['results']
    
    def post_tool_configuration(self,name,tool_type,description=None,url=None,authentication_type=None,extras=None,username=None,password=None,auth_title=None,ssh=None,api_key=None):
        """

        Receives Tool type configurations

        authentication_type can be "API", "Password" or "SSH"

        """
        data = {}

        data["name"] = name
        data["tool_type"] = tool_type

        if description:
            data["description"] = description

        if description:
            data["description"] = description

        if url:
            data["url"] = url

        if authentication_type:
            data["authentication_type"] = authentication_type

        if extras:
            data["extras"] = extras

        if username:
            data["username"] = username

        if password:
            data["password"] = password

        if auth_title:
            data["auth_title"] = auth_title
        
        if ssh:
            data["ssh"] = ssh
        
        if api_key:
            data["api_key"] = api_key
        
        return self._request('POST', 'tool_configurations/',data=data)
    
    ###### Product_members API #####
    def get_product_members(self,id=None,limit=10000,prefetch=None,product_id=None,user_id=None):
        """ 
        get list of members of a products.
        id: integer
        limit: limit the list of result to be fetched
        prefetch: List of fields for which to prefetch model instances and add those to the response. it can be [product,role,user]
        product_id: integer, id of a product
        user_id: integer, id of a user
        """
        params={}
        if id:
            params['id'] = id
        
        if limit:
            params['limit'] = limit
        
        if prefetch:
            params['prefetch'] =prefetch
        
        if product_id:
            params['product_id'] = product_id
            
        if user_id:
            params['user_id'] = user_id
        
        return self._request('GET','product_members/',params)
    
    def add_product_member(self,product,user,role,prefetch={}):
        """ Add an user to a product
            product: product id
            user: user id
            role: interger(1-5) 1:API_importer, 2:writer, 3:Maintainer, 4:Owner, 5:Reader  
        """
        data = {
            'product': product, 
            'user': user, 
            'role': role, 
            'prefetch': prefetch
            }
        return self._request('POST','product_members/', data=data)
        
    def edit_product_member(self,id,product,user,role,prefetch={}):
        """ edit an user to a product
                id: A unique integer value identifying this product_ member. This can be accessed through get_product_members
                product: product id
                user: user id
                role: interger(1-5) 1:API_importer, 2:writer, 3:Maintainer, 4:Owner, 5:Reader  
            """
        data = {
                'product': product, 
                'user': user, 
                'role': role, 
                'prefetch': prefetch
                }
        return self._request('PUT','product_members/' + str(id) + '/',data=data)      
    
    def delete_product_member(self,user_id):
        """ Delete a product member

        Args:
            user_id (int): A unique integer value identifying this product_ member.

        Returns:
            response
        """
        return self._request('DELETE','product_members/'+ str(user_id) + '/')      
        
    ###### Test API #######
    def list_tests(self, name=None, engagement_in=None, test_type=None, limit=20000, offset=None):
        """Retrieves all the tests.

        :param name_contains: Search by product name.
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if offset:
            params['offset'] = offset

        if engagement_in:
            params['engagement'] = engagement_in

        if test_type:
            params['test_type'] = test_type

        return self._request('GET', 'tests/', params)

    def get_last_test_id(self, engagement_in=None):
        """Retrieves the last test of a engagement

        """

        params  = {}

        if engagement_in:
            params['engagement'] = engagement_in

        totaltests = self.list_tests(engagement_in=engagement_in,limit=1).data["count"]

        params['offset'] = totaltests - 1
        params['prefetch'] = ""

        if totaltests != 0:
            return self._request('GET', 'tests/', params).data["results"][0]["id"]
        else:
            return None
    
    def list_test_types(self, name=None,limit=20000):
        params = {}
        if limit:
            params['limit'] = limit
        if name:
            params['name'] = name
        return self._request('GET', 'test_types/',params)

    def list_test_ids(self, engagement_id):
        test_list=self.list_tests(engagement_in=engagement_id)
        tests=test_list.data['results']
        output=[]
        for iterator in tests:
            output.append(iterator['id'])
        return output

    def get_test(self, test_id):
        """Retrieves a test using the given test id.

        :param test_id: Test identification.

        """
        return self._request('GET', 'tests/' + str(test_id) + '/')

    def get_test_type(self, test_type_id):
        """Retrieves a test using the given test id.

        :param test_id: Test identification.

        """
        return self._request('GET', 'test_types/' + str(test_type_id) + '/')
    
    def delete_preview_test(self,test_id,limit=2000000):
        """checks if a test can be safely deleted"""
        params = {}
        if limit:
            params['limit'] = limit
        
        return self._request('GET',f'tests/{test_id}/delete_preview/', params).data['results']
    
    def delete_test(self,test_id):
        """deletes a test"""
        return self._request('DELETE', 'tests/' + str(test_id) + '/')
    
    def create_test(self, engagement_id, test_type, environment, target_start, target_end, percent_complete=None):
        """Creates a product with the given properties.

        :param engagement_id: Engagement id.
        :param test_type: Test type key id.
        :param target_start: Test start date.
        :param target_end: Test end date.
        :param percent_complete: Percentage until test completion.

        """

        data = {
            'engagement': engagement_id,
            'test_type': test_type,
            'environment': environment,
            'target_start': target_start,
            'target_end': target_end,
            'percent_complete': percent_complete
        }

        return self._request('POST', 'tests/', data=data)

    def set_test(self, test_id, engagement_id=None, test_type=None, environment=None,
        target_start=None, target_end=None, percent_complete=None):
        """Creates a product with the given properties.

        :param engagement_id: Engagement id.
        :param test_type: Test type key id.
        :param target_start: Test start date.
        :param target_end: Test end date.
        :param percent_complete: Percentage until test completion.

        """

        current_test = self.get_test(test_id).data

        data = {}

        if engagement_id:
            data['engagement'] = engagement_id

        if test_type:
            data['test_type'] = test_type

        if environment:
            data['environment'] = environment

        if target_start:
            data['target_start'] = target_start
        else:
            data['target_start'] = current_test["target_start"]

        if target_end:
            data['target_end'] = target_end
        else:
            data['target_end'] = current_test["target_end"]

        if percent_complete:
            data['percent_complete'] = percent_complete

        return self._request('PUT', 'tests/' + str(test_id) + '/', data=data)

    ###### Findings API #######
    def list_findings(self, id=None, active=None, is_mitigated=None, duplicate=None, mitigated=None, severity=None, verified=None, severity_lt=None,
        severity_gt=None, severity_contains=None, title=None, url_contains=None, date_lt=None,
        date_gt=None, date=None, product_id_in=None, engagement_id_in=None, test_id_in=None, build=None,found_by=None, related_fields=None, offset=None, limit=20000):

        """Returns filtered list of findings.

        :param active: Finding is active: (true or false)
        :param duplicate: Duplicate finding (true or false)
        :param is_mitigated: Mitigated finding (true or false)
        :param severity: Severity: Low, Medium, High and Critical.
        :param verified: Finding verified.
        :param severity_lt: Severity less than Low, Medium, High and Critical.
        :param severity_gt: Severity greater than Low, Medium, High and Critical.
        :param severity_contains: Severity contains: (Medium, Critical)
        :param title_contains: Filter by title containing the keyword.
        :param url_contains: Filter by URL containing the keyword.
        :param date_lt: Date less than.
        :param date_gt: Date greater than.
        :param date: Return findings for a particular date.
        :param product_id_in: Product id(s) associated with a finding. (1,2 or 1)
        :param engagement_id_in: Engagement id(s) associated with a finding. (1,2 or 1)
        :param test_in: Test id(s) associated with a finding. (1,2 or 1)
        :param build_id: User specified build id relating to the build number from the build server. (Jenkins, Travis etc.).
        :param limit: Number of records to return.
        :param found_by: specify the scanner of the findins

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if id:
            params['id'] = id

        if active:
            params['active'] = active

        if duplicate:
            params['duplicate'] = duplicate

        if mitigated:
            params['mitigated'] = mitigated

        if severity:
            params['severity'] = severity

        if verified:
            params['verified'] = verified

        if severity_lt:
            params['severity__lt'] = severity_lt

        if severity_gt:
            params['severity__gt'] = severity_gt

        if severity_contains:
            params['severity__contains'] = severity_contains

        if title:
            params['title'] = title

        if url_contains:
            params['url__contains'] = url_contains

        if date_lt:
            params['date__lt'] = date_lt

        if date_gt:
            params['date__gt'] = date_gt

        if date:
            params['date'] = date

        if engagement_id_in:
            params['test__engagement'] = engagement_id_in

        if product_id_in:
            params['test__engagement__product'] = product_id_in

        if test_id_in:
            params['test'] = test_id_in

        if build:
            params['build_id__contains'] = build

        if related_fields:
            params['related_fields']=related_fields

        if found_by:
            params['found_by'] = found_by

        if is_mitigated:
            params['is_mitigated'] = is_mitigated

        if offset:
            params['offset'] = offset

        return self._request('GET', 'findings/', params)

    def get_finding(self, finding_id,related_fields="false"):
        """
        Retrieves a finding using the given finding id.
        :param finding_id: Finding identification.
        """
        return self._request('GET', 'findings/' + str(finding_id) + '/?related_fields='+related_fields)

    def create_finding(self, title, description, severity, cwe, date, product_id, engagement_id,
        test_id, user_id, impact, active, verified, mitigation, references=None, build=None, line=0,
        file_path=None, static_finding="False", dynamic_finding="False", false_p="False",
        duplicate="False",  out_of_scope="False", under_review="False", under_defect_review="False",
        numerical_severity=None, found_by=None, tags=None):
        """Creates a finding with the given properties.
        :param title: Finding title
        :param description: Finding detailed description.
        :param severity: Finding severity: Low, Medium, High and Critical
        :param cwe: CWE (int)
        :param date: Discovered Date.
        :param product_id: Product finding should be associated with.
        :param engagement_id: Engagement finding should be associated with.
        :param test_id: Test finding should be associated with.
        :param user_id: Reporter of finding.
        :param impact: Detailed impact of finding.
        :param active: Finding active and reported on.
        :param verified: Finding has been verified.
        :param mitigation: Steps to mitigate the finding.
        :param references: Details on finding.
        :param build: User specified build id relating to the build number from the build server. (Jenkins, Travis etc.).
        """
        
        #If numerical_severity is not set, maps numerical_severity with severity : Low then S0 Medium then S1....
        if (numerical_severity is None):
            if (severity=='Low'): numerical_severity='S1'
            elif (severity=='Medium'): numerical_severity='S2'
            elif (severity=='High'): numerical_severity='S3'
            elif (severity=='Critical'): numerical_severity='S4'


        data = {
            'title': title,
            'description': description,
            'severity': severity,
            'cwe': cwe,
            'date': date,
            'product': product_id,
            'engagement': engagement_id,
            'test': test_id,
            'reporter': user_id,
            'impact': impact,
            'active': active,
            'verified': verified,
            'mitigation': mitigation,
            'references': references,
            'build_id' : build,
            'line' : line,
            'file_path' : file_path,
            'static_finding' : static_finding,
            'dynamic_finding' : dynamic_finding,
            'false_p' : false_p,
            'duplicate' : duplicate,
            'out_of_scope' : out_of_scope,
            'under_review' : under_review,
            'under_defect_review' : under_defect_review,
            'numerical_severity' : numerical_severity,
            'found_by' : [] if found_by is None else found_by,
            'tags': [] if tags is None else tags
        }
        return self._request('POST', 'findings/', data=data)

    def set_finding(self, finding_id, product_id, engagement_id, test_id, title=None, description=None, severity=None,
        cwe=None, date=None, user_id=None, impact=None, active=None, verified=None,
        mitigation=None, references=None, build=None):

        """Updates a finding with the given properties.

        :param title: Finding title
        :param description: Finding detailed description.
        :param severity: Finding severity: Low, Medium, High and Critical
        :param cwe: CWE (int)
        :param date: Discovered Date.
        :param product_id: Product finding should be associated with.
        :param engagement_id: Engagement finding should be associated with.
        :param test_id: Test finding should be associated with.
        :param user_id: Reporter of finding.
        :param impact: Detailed impact of finding.
        :param active: Finding active and reported on.
        :param verified: Finding has been verified.
        :param mitigation: Steps to mitigate the finding.
        :param references: Details on finding.
        :param build: User specified build id relating to the build number from the build server. (Jenkins, Travis etc.).

        """

        data = {}

        if title:
            data['title'] = title

        if description:
            data['description'] = description

        if severity:
            data['severity'] = severity

        if cwe:
            data['cwe'] = cwe

        if date:
            data['date'] = date

        if product_id:
            data['product'] = product_id

        if engagement_id:
            data['engagement'] = engagement_id

        if test_id:
            data['test'] = test_id

        if user_id:
            data['reporter'] = user_id

        if impact:
            data['impact'] = impact

        if active:
            data['active'] = active

        if verified:
            data['verified'] = verified

        if mitigation:
            data['mitigation'] = mitigation

        if references:
            data['references'] = references

        if build:
            data['build_id'] = build

        return self._request('PUT', 'findings/' + str(finding_id) + '/', data=data)

    def patch_finding(self, finding_id, product_id=None,engagement_id=None, is_mitigated=None, test_id=None, title=None, description=None, severity=None, cwe=None, date=None, user_id=None, impact=None, active=None, verified=None, mitigation=None, references=None, build=None,false_p=None, risk_accepted=None, cvssv3_score=None, cvssv3=None):
        data = {}

        if title is not None:
            data['title'] = title

        if is_mitigated is not None:
            data['is_mitigated'] = is_mitigated

        if description is not None:
            data['description'] = description

        if severity is not None:
            data['severity'] = severity

        if cwe is not None:
            data['cwe'] = cwe

        if date is not None:
            data['date'] = date

        if product_id is not None:
            data['product'] = product_id

        if engagement_id is not None:
            data['engagement'] = engagement_id

        if test_id is not None:
            data['test'] = test_id

        if user_id is not None:
            data['reporter'] = user_id

        if impact is not None:
            data['impact'] = impact

        if active is not None:
            data['active'] = active

        if verified is not None:
            data['verified'] = verified

        if mitigation is not None:
            data['mitigation'] = mitigation

        if references is not None:
            data['references'] = references

        if build is not None:
            data['build_id'] = build
        
        if false_p is not None:
            data['false_p']=false_p
        
        if risk_accepted is not None:
            data['risk_accepted'] = risk_accepted
        
        if cvssv3_score is not None:
            data['cvssv3_score'] = cvssv3_score
        
        if cvssv3 is not None:
            data['cvssv3'] = cvssv3

        return self._request('PATCH', 'findings/' + str(finding_id) + '/', data=data)
    
    def delete_findings(self,finding_id):
        return self._request('DELETE', 'findings/' +str(finding_id) + "/")
    
    def accept_risks(self,vulnerability_id,accepted_by,justification=None):
        data = {}
        if vulnerability_id is not None:
            data['vulnerability_id'] = vulnerability_id
        if justification is not None:
            data['justification'] = justification
        if accepted_by is not None:
            data['accepted_by'] = accepted_by

        return self._request('POST', 'findings/accept_risks/', data=[data])

    def finding_add_note(self,finding_id,entry,private=None,note_type=None):
        data = {}
        data['entry'] = entry
        if private is not None:
            data['private'] = private
        if note_type is not None:
            data['note_type'] = note_type

        return self._request('POST', 'findings/ '+ str(finding_id) +'/notes/', data=data)

    def finding_get_note(self,finding_id):
        return self._request('GET', 'findings/ '+ str(finding_id) +'/notes/')

    def close_finding(self, finding_id, is_mitigated=True, mitigated=None, false_p=False, out_of_scope=False, duplicate=False):

        """Closes an finding with the given properties."""
        data = {}

        data['is_mitigated'] = True

        if mitigated == None:
            data['mitigated'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%s")
        if false_p != None:
            data['false_p'] = false_p
        if out_of_scope != None:
            data['out_of_scope'] = out_of_scope
        if duplicate != None:
            data['duplicate'] = duplicate

        return self._request('POST', 'findings/' +str(finding_id) + "/close/", data=data)

    ##### SLA Configurations API #####
    def get_sla_configurations(self):
        """Get SLA Configurations"""
        return self._request('GET', 'sla_configurations/')

    def post_sla_configurations(self, name, description, critical, high, medium, low):
        """
        Create a application analysis to product mapping.
        :param id: Language identification.
        """
        data = {
            'name': name,
            'description': description,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        }
        return self._request('POST', 'sla_configurations/', data=data)

    def put_sla_configurations(self, id, name=None, description=None, critical=None, high=None, medium=None, low=None):
        """
        Create a application analysis to product mapping.
        :param id: Language identification.
        """
        data = {
            'name': name,
            'description': description,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        }
        return self._request('PUT', 'sla_configurations/'+ str(id), data=data)

    ##### System Settings API #####
    def get_system_settings(self):
        """Get System Settings"""

        return self._request('GET', 'system_settings/')

    def put_system_settings(self, enable_slack_notifications=False,  enable_auditlog=True, enable_deduplication=False, delete_dupulicates=False, max_dupes=0, s_finding_severity_naming=False, false_positive_history= False, display_endpoint_uri=False, enable_jira=False, enable_benchmark=True, enable_template_match= False, engagement_auto_close = False, engagement_auto_close_days= False, enable_product_grade=False, product_grade_a=False, product_grade_b=False, product_grade_c=False, product_grade_d=False, product_grade_f=False, enable_finding_sla=True, sla_critical=30, sla_high=60, sla_medium=90, sla_low=180):
        """
        :param enable_auditlog: DefectDojo maintains an audit log for changes made to entities
        :param enable_deduplication: Deduplicate findings by comparing the findings.
        :param delete_dupulicates: Duplicate findings will be deleted
        :param max_dupes: Maximum number of saved duplicates before deletion
        :param enable_jira: Enables JIRA integration
        :param enable_benchmark: Enables Benchmarks such as OWASP ASVS
        :param enable_product_grade: Displays a grade letter next to a product to show overall health
        :param enable_finding_sla: Enable finding SLAs for time to remediate
        """
        data = {
            'enable_slack_notifications':enable_slack_notifications,
            'enable_auditlog': enable_auditlog,
            'enable_deduplication': enable_deduplication,
            'delete_dupulicates': delete_dupulicates,
            'max_dupes': max_dupes,
            'enable_jira': enable_jira,
            's_finding_severity_naming': s_finding_severity_naming,
            'false_positive_history': false_positive_history,
            'display_endpoint_uri': display_endpoint_uri,
            'enable_benchmark': enable_benchmark,
            'enable_template_match': enable_template_match,
            'engagement_auto_close': engagement_auto_close,
            'engagement_auto_close_days': engagement_auto_close_days,
            'enable_product_grade': enable_product_grade,
            'product_grade_a': product_grade_a,
            'product_grade_b': product_grade_b,
            'product_grade_c': product_grade_c,
            'product_grade_d': product_grade_d,
            'product_grade_f': product_grade_f,
            'enable_finding_sla': enable_finding_sla,
            'sla_critical': sla_critical,
            'sla_high': sla_high,
            'sla_medium': sla_medium,
            'sla_low': sla_low
        }
        return self._request('PUT', 'system_settings/1/', data=data)

    def patch_system_settings(self, enable_auditlog=None, enable_deduplication=None, delete_dupulicates=None, max_dupes=None, enable_jira=None, s_finding_severity_naming = None, false_positive_history = None, display_endpoint_uri = None, enable_benchmark=None, enable_template_match = None, engagement_auto_close = None, engagement_auto_close_days = None, enable_product_grade=None, product_grade_a = None, product_grade_b = None, product_grade_c = None, product_grade_d = None, product_grade_f = None, enable_finding_sla=None, sla_critical=None, sla_high=None, sla_medium=None, sla_low=None):
        """
        :param enable_auditlog: DefectDojo maintains an audit log for changes made to entities
        :param enable_deduplication: Deduplicate findings by comparing the findings.
        :param delete_dupulicates: Duplicate findings will be deleted
        :param max_dupes: Maximum number of saved duplicates before deletion
        :param enable_jira: Enables JIRA integration
        :param enable_benchmark: Enables Benchmarks such as OWASP ASVS
        :param enable_product_grade: Displays a grade letter next to a product to show overall health
        :param enable_finding_sla: Enable finding SLAs for time to remediate
        """
        data = {}
        if enable_auditlog is not None:
            data['enable_auditlog'] = enable_auditlog

        if enable_deduplication is not None:
            data['enable_deduplication'] = enable_deduplication

        if delete_dupulicates is not None:
            data['delete_dupulicates'] = delete_dupulicates

        if max_dupes is not None:
            data['max_dupes'] = max_dupes

        if enable_jira is not None:
            data['enable_jira'] = enable_jira

        if s_finding_severity_naming is not None:
            data['s_finding_severity_naming'] = s_finding_severity_naming

        if false_positive_history is not None:
            data['false_positive_history'] = false_positive_history

        if display_endpoint_uri is not None:
            data['display_endpoint_uri'] = display_endpoint_uri

        if enable_benchmark is not None:
            data['enable_benchmark'] = enable_benchmark

        if enable_template_match is not None:
            data['enable_template_match'] = enable_template_match

        if engagement_auto_close is not None:
            data['engagement_auto_close'] = engagement_auto_close

        if engagement_auto_close_days is not None:
            data['engagement_auto_close_days'] = engagement_auto_close_days

        if enable_product_grade is not None:
            data['enable_product_grade'] = enable_product_grade

        if product_grade_a is not None:
            data['product_grade_a'] = product_grade_a

        if product_grade_b is not None:
            data['product_grade_b'] = product_grade_b

        if product_grade_c is not None:
            data['product_grade_c'] = product_grade_c

        if product_grade_d is not None:
            data['product_grade_d'] = product_grade_d

        if product_grade_f is not None:
            data['product_grade_f'] = product_grade_f

        if enable_finding_sla is not None:
            data['enable_finding_sla'] = enable_finding_sla

        if sla_critical is not None:
            data['sla_critical:'] = sla_critical

        if sla_high is not None:
            data['sla_high:'] = sla_high

        if sla_medium is not None:
            data['sla_medium:'] = sla_medium

        if sla_low is not None:
            data['sla_low:'] = sla_low

        return self._request('PATCH', 'system_settings/1/', data=data)

    ##### Build Details API #####
    def build_details(self, engagement_id, json):
        """Uploads commit file changes to an engagement.

        :param engagement_id: Engagement identifier.
        :param file: File/Json with meta data to be uploaded.

        """

        data = {
            'file': json,
            'engagement': ('', engagement_id)
        }

        return self._request(
            'POST', 'build_details/',
            files=data
        )

    ##### Upload API #####

    def upload_scan(self, engagement_id, scan_type, active, verified, close_old_findings, skip_duplicates, scan_date, file=None, tags=None, build=None, minimum_severity="Low", deduplication_on_engagement=True, close_old_findings_product_scope=False):
        """Uploads and processes a scan file.

        :param application_id: Application identifier.
        :param file_path: Path to the scan file to be uploaded.

        """

        if build is None:
            build = ''
        
        if self.debug and file:
            print("filedata:")
            print(file)

        data = {
            'engagement': ('', engagement_id),
            'scan_type': ('', scan_type),
            'active': ('', active),
            'verified': ('', verified),
            'close_old_findings': ('', close_old_findings),
            'skip_duplicates': ('', skip_duplicates),
            'scan_date': ('', scan_date),
            'build_id': ('', build),
            'minimum_severity': ('', minimum_severity),
            'deduplication_on_engagement': ('', deduplication_on_engagement),
            'close_old_findings_product_scope' : ('', close_old_findings_product_scope)
        }

        if tags != None:
            data["tags"] = tags

        if file != None:
            with open(file, 'rb') as f:
                filedata = f.read()
            data["file"] = filedata

        """
        TODO: implement these parameters:
          lead
          test_type
          scan_date
        """
        return self._request(
            'POST', 'import-scan/',
            files=data
        )

    ##### Re-upload API #####

    def reupload_scan(self, file, scan_type, test= None, active=None, scan_date=None, tags=None, verified=None, do_not_reactivate=None, 
                      endpoint_to_add=None, product_type_name=None, product_name=None, engagement_name=None, engagement_end_date=None, source_code_management_uri=None, 
                      test_title=None, auto_create_context=None, deduplication_on_engagement=None, push_to_jira=None, close_old_findings=None, 
                      close_old_findings_product_scope=None, build_id=None, api_scan_configuration=None, service=None, 
                      lead=None, group_by=None, create_finding_groups_for_all_findings=None, engagement_id=None, product_id=None, product_type_id=None, 
                      build=None, version=None, branch_tag=None, commit_hash=None,
                      minimum_severity="Info", auto_group_by=None, environment=None):
        """Re-uploads and processes a scan file.

        :param test_id: Test identifier.
        :param file: Path to the scan file to be uploaded.

        """
        if build is None:
            build = ''

        data = {
            'test': ('', test),
            'file': open(file, 'rb'),
            'scan_type': ('', scan_type),
            'active': ('', active),
            'scan_date': ('', scan_date),
            'tags': ('', tags),
            'commit_hash': ('', commit_hash),
	        'minimum_severity': ('', minimum_severity),
            'verified': ('', verified),
            'do_not_reactivate': ('', do_not_reactivate),
            'endpoint_to_add': ('', endpoint_to_add),
            'product_type_name': ('', product_type_name),
            'product_name': ('', product_name),
            'engagement_name': ('', engagement_name),
            'engagement_end_date': ('', engagement_end_date),
            'source_code_management_uri': ('', source_code_management_uri),
            'test_title': ('', test_title),
            'auto_create_context': ('', auto_create_context),
            'deduplication_on_engagement': ('', deduplication_on_engagement),
            'push_to_jira': ('', push_to_jira),
            'close_old_findings': ('', close_old_findings),
            'close_old_findings_product_scope': ('', close_old_findings_product_scope),
            'version': ('', version),
            'build_id': ('', build_id),
            'branch_tag': ('', branch_tag),
            'api_scan_configuration': ('', api_scan_configuration),
            'service': ('', service),
            'environment': ('', environment),
            'lead': ('', lead),
            'group_by': ('', group_by),
            'create_finding_groups_for_all_findings': ('', create_finding_groups_for_all_findings),
            'engagement_id': ('', engagement_id),
            'product_id': ('', product_id),
            'product_type_id': ('', product_type_id),
        }

        if auto_group_by:
            data['auto_group_by'] = (auto_group_by, '')

        if tags != None:
            data["tags"] = tags

        if file != None:
            with open(file, 'rb') as f:
                filedata = f.read()
            data["file"] = filedata

        return self._request(
            'POST', 'reimport-scan/',
            files=data
        )        

    ##### Credential API #####

    def list_credentials(self, name=None, username=None, limit=20000):
        """Retrieves all the globally configured credentials.
        :param name_contains: Search by credential name.
        :param username: Search by username
        :param limit: Number of records to return.
        """

        params  = {}
        if limit:
            params['limit'] = limit

        if name:
            params['name__contains'] = name

        if username:
            params['username__contains'] = username

        return self._request('GET', 'credentials/', params)

    def get_credential(self, cred_id, limit=20000):
        """
        Retrieves a credential using the given credential id.
        :param credential_id: Credential identification.
        """
        return self._request('GET', 'credentials/' + str(cred_id) + '/')

    ##### Credential Mapping API #####

    def list_credential_mappings(self, name=None, product_id_in=None, engagement_id_in=None, test_id_in=None, finding_id_in=None, limit=20000):
        """Retrieves mapped credentials.

        :param name_contains: Search by credential name.
        :param username: Search by username
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if name:
            params['name'] = name

        if product_id_in:
            params['product__id__in'] = product_id_in

        if engagement_id_in:
            params['engagement__id__in'] = engagement_id_in

        if test_id_in:
            params['test__id__in'] = test_id_in

        if finding_id_in:
            params['finding__id__in'] = finding_id_in

        return self._request('GET', 'credential_mappings/', params)

    def get_credential_mapping(self, cred_mapping_id, limit=20000):
        """
        Retrieves a credential using the given credential id.
        :param cred_mapping_id: Credential identification.
        """
        return self._request('GET', 'credential_mappings/' + str(cred_mapping_id) + '/')

    ##### App Analysis API #####
    def list_app_analysis(self, id=None, product_id=None, language_name=None, limit=20000):
        """Retrieves source code languages.

        :param id: Search by lanaguage id.
        :param product: Search by product id
        :param language_name: Search by language name
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if id:
            params['id'] = id

        if product_id:
            params['product__id'] = product_id

        if language_name:
            params['name__icontains'] = language_name

        return self._request('GET', 'app_analysis/', params)

    def create_app_analysis(self, product_id, user_id, name, confidence, version, icon, website):
        """
        Create a application analysis to product mapping.
        :param id: Language identification.
        """

        data = {
            'product': product_id,
            'user': user_id,
            'name': name,
            'confidence': confidence,
            'version': version,
            'icon': icon,
            'website': website
        }

        return self._request('POST', 'app_analysis/', data=data)

    def delete_app_analysis(self, id):
        """
        Deletes an app analysis using the given id.
        :param id: Language identification.
        """
        return self._request('DELETE', 'app_analysis/' + str(id) + '/')

    def delete_all_app_analysis_product(self, product_id):
        """
        Delete all app analysis using the given id.
        :product_id id: Product to remove
        """
        app_analysis = self.list_app_analysis(product_id=product_id)

        if app_analysis.success:
            for app in app_analysis.data["objects"]:
                self.delete_app_analysis(self.get_id_from_url(app['resource_uri']))

    ##### Language API #####

    def list_languages(self, id=None, product_id=None, language_name=None, limit=20000):
        """Retrieves source code languages.

        :param id: Search by lanaguage id.
        :param product: Search by product id
        :param language_name: Search by language name
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if id:
            params['id'] = id

        if product_id:
            params['product__id'] = product_id

        if language_name:
            params['language_type__language__icontains'] = language_name

        return self._request('GET', 'languages/', params)

    def create_language(self, product_id, user_id, files, code, blank, comment, language_type_id=None, language_name=None):
        """
        Create a language to product mapping.
        :param product_id: Product identification.
        """
        #If language name specified then lookup
        if language_name:
            languages = self.list_language_types(language_name=language_name)

            if languages.success:
                for language in languages.data["objects"]:
                    language_type = language['resource_uri']

        data = {
            'product': product_id,
            'language_type': language_type,
            'user': user_id,
            'files': files,
            'code': code,
            'blank': blank,
            'comment': comment
        }

        return self._request('POST', 'languages/', data=data)

    def delete_language(self, id):
        """
        Deletes a language using the given id.
        :param id: Language identification.
        """
        return self._request('DELETE', 'languages/' + str(id) + '/')

    def delete_all_languages_product(self, product_id):
        """
        Delete all languages for a given product id.
        :param id: Language identification.
        """
        languages = self.list_languages(product_id=product_id)

        if languages.success:
            for language in languages.data["objects"]:
                self.delete_language(self.get_id_from_url(language['resource_uri']))

    def list_language_types(self, id=None, language_name=None, limit=20000):
        """Retrieves source code languages.

        :param id: Search by lanaguage id.
        :param language_name: Search by language name
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if id:
            params['id'] = id

        if language_name:
            params['language__icontains'] = language_name

        return self._request('GET', 'language_types/', params)

    ###### Tool API #######

    def list_tool_types(self, resource_id=None, name=None, limit=20000):
        """Retrieves all the tool types.

        :param name_contains: Search by tool type name.
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if resource_id:
            params['id'] = resource_id

        if name:
            params['name__contains'] = name

        return self._request('GET', 'tool_types/', params)

    def list_tools(self, resource_id=None, name=None, tool_type_id=None, url=None, name_icontains=None, limit=20000):
        """Retrieves all the tool configurations.

        :param name_contains: Search by tool name.
        :param tool_type_id: Search by tool type id
        :param url: Search by url
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if resource_id:
            params['id'] = resource_id

        if name:
            params['name'] = name

        if tool_type_id:
            params['tool_type__id'] = tool_type_id

        if tool_type_id:
            params['url__contains'] = tool_type_id

        if name_icontains:
            params['name__icontains'] = name_icontains

        return self._request('GET', 'tool_configurations/', params)

    def list_tool_products(self, resource_id=None, url=None, name=None, tool_configuration_id=None,
        tool_project_id=None, product_id=None, limit=20000):
        """Retrieves all the tools.

        :param url_contains: Search by url.
        :param name_contains: Search by tool name.
        :param tool_configuration_id: Search by tool_configuration_id
        :param tool_project_id: Search by tool_project_id
        :param product_id: Search by product_id
        :param limit: Number of records to return.

        """

        params  = {}
        if limit:
            params['limit'] = limit

        if resource_id:
            params['id'] = resource_id

        if name:
            params['name'] = name

        if url:
            params['url__iregex'] = url

        if tool_project_id:
            params['tool_project_id__contains'] = tool_project_id

        if tool_configuration_id:
            params['tool_configuration__id'] = tool_configuration_id

        if product_id:
            params['product__id'] = product_id

        return self._request('GET', 'tool_product_settings/', params)
    
    #Risk Acceptance

    def delete_risk_accepance(self,id):
        """ Delete a Risk Acceptance

        Args:
            id (int): A unique integer value identifying this risk acceptance.

        Returns:
            response
        """
        return self._request('DELETE','risk_acceptance/'+ str(id) + '/')

    # Utility

    @staticmethod
    def _build_list_params(param_name, key, values):
        """Builds a list of POST parameters from a list or single value."""
        params = {}
        if hasattr(values, '__iter__'):
            index = 0
            for value in values:
                params[str(param_name) + '[' + str(index) + '].' + str(key)] = str(value)
                index += 1
        else:
            params[str(param_name) + '[0].' + str(key)] = str(values)
        return params

    def _request(self, method, url, params=None, data=None, files=None):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        if data:
            data = json.dumps(data)

        headers = {
            'User-Agent': self.user_agent,
            'Authorization' : (("ApiKey "+ self.user + ":" + self.api_token) if (self.api_version=="v1") else ("Token " + self.api_token))
        }

        if not files:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'

        if self.proxies:
            proxies=self.proxies
        else:
            proxies = {}

        try:
            if self.debug:
                print("request:")
                print(method + ' ' + url)
                print("headers: " + str(headers))
                print("params:" + str(params))
                print("data:" + str(data))
                print("files:" + str(files))

            response = requests.request(method=method, url=self.host + url, params=params, data=data, files=files, headers=headers,
                                        timeout=self.timeout, verify=self.verify_ssl, cert=self.cert, proxies=proxies)

            if self.debug:
                print("response:")
                print(response.status_code)
                print(response.text)

            try:
                if response.status_code == 201: #Created new object
                    try:
                        object_id = response.headers["Location"].split('/')
                        key_id = object_id[-2]
                        data = int(key_id)
                    except:
                        data = response.json()

                    return DefectDojoResponse(message="Upload complete", response_code=response.status_code, data=data, success=True)
                elif response.status_code == 204: #Object updates
                    return DefectDojoResponse(message="Object updated.", response_code=response.status_code, success=True)
                elif response.status_code == 400: #Object not created
                    return DefectDojoResponse(message="Error occured in API.", response_code=response.status_code, success=False, data=response.text)
                elif response.status_code == 404: #Object not created
                    return DefectDojoResponse(message="Object id does not exist.", response_code=response.status_code, success=False, data=response.text)
                elif response.status_code == 401:
                    return DefectDojoResponse(message="Unauthorized.", response_code=response.status_code, success=False, data=response.text)
                elif response.status_code == 414:
                    return DefectDojoResponse(message="Request-URI Too Large.", response_code=response.status_code, success=False)
                elif response.status_code == 500:
                    return DefectDojoResponse(message="An error 500 occured in the API.", response_code=response.status_code, success=False, data=response.text)
                elif response.status_code == 504:
                    return DefectDojoResponse(message="An error 504 occured in the API.", response_code=response.status_code, success=False, data=response.text)
                else:
                    data = response.json()
                    return DefectDojoResponse(message="Success", data=data, success=True, response_code=response.status_code)
            except ValueError:
                return DefectDojoResponse(message='JSON response could not be decoded.', response_code=response.status_code, success=False, data=response.text)
        except requests.exceptions.SSLError:
            print("An SSL error occurred.")
            return DefectDojoResponse(message='An SSL error occurred.', response_code=response.status_code, success=False)
        except requests.exceptions.ConnectionError:
            print("A connection error occurred.")
            return DefectDojoResponse(message='A connection error occurred.', response_code=response.status_code, success=False)
        except requests.exceptions.Timeout:
            print("The request timed out")
            return DefectDojoResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.', response_code=response.status_code,
                                     success=False)
        except requests.exceptions.RequestException as e:
            print("There was an error while handling the request.")
            print(e)
            return DefectDojoResponse(message='There was an error while handling the request.', response_code=response.status_code, success=False)


class DefectDojoResponse(object):
    """
    Container for all DefectDojo API responses, even errors.

    """

    def __init__(self, message, success, data=None, response_code=-1):
        self.message = message
        self.data = data
        self.success = success
        self.response_code = response_code

    def __str__(self):
        if self.data:
            return str(self.data)
        else:
            return self.message

    def id(self):
        print("response_code" + str (self.response_code))
        if self.response_code == 400: #Bad Request
            raise ValueError('Object not created:' + json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': ')))
        return int(self.data["id"])

    def count(self):
        return self.data["count"]

    def data_json(self, pretty=False):
        """Returns the data as a valid JSON string."""
        if pretty:
            return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.data)
