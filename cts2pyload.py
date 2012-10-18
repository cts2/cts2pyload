#!/usr/bin/env python
'''
Utility file to load CTS2 Resources.
'''
__author__ = "Kevin Peterson"
__credits__ = ["Harold Solbrig"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Kevin Peterson"
__email__ = "kevin.peterson@mayo.edu"

import urllib2
import base64
import argparse
import os
import codecs
from xml.dom.minidom import parseString

UPDATES_NS = 'http://schema.omg.org/spec/CTS2/1.0/Updates'

CHANGE_SET_CREATE = "/changeset"

create_urls = {   
      "CodeSystemCatalogEntry" : "/codesystem",
      "CodeSystemVersionCatalogEntry" : "/codesystemversion",
      "ValueSetCatalogEntry" : "/valueset",
      "ValueSetDefinition" : "/valuesetdefinition",
      "ResolvedValueSet" : "/resolvedvalueset",
      "EntityDescription" : "/entity",
      "MapCatalogEntry" : "/map",
      "MapVersion" : "/mapversion",
      "MapEntry" : "/mapentry",
      "ConceptDomainCatalogEntry" : "/conceptdomain",
      "ConceptDomainBinding" : "/conceptdomainbinding",
      "Association" : "/association"
}

COMMIT_CHANGE_SET_XML = '''
<?xml version="1.0" encoding="UTF-8"?>
<UpdateChangeSetMetadataRequest
    xmlns="http://schema.omg.org/spec/CTS2/1.0/CoreService"
    xmlns:core="http://schema.omg.org/spec/CTS2/1.0/Core"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.omg.org/spec/CTS2/1.0/CoreService http://informatics.mayo.edu/svn/trunk/cts2/spec/psm/rest/serviceSchema/CoreService.xsd">
    <updatedState>
        <state>FINAL</state>
    </updatedState>
</UpdateChangeSetMetadataRequest>
'''

def get(url,username,password):   
    '''GET a Resource'''
    req = urllib2.Request(url=url, 
                      headers={'Content-Type': 'application/xml',
                               'Authorization' : 'Basic %s' % base64.encodestring('%s:%s' % (username, password))[:-1]
                      })
                      
    return urllib2.urlopen(req).read()

def post(url,username,password,data):   
    '''POST a Resource'''
    if(data is not None):
        data = unicode(data.strip(), 'utf8')
    
    req = urllib2.Request(url=url, 
                      data=data,
                      headers={'Content-Type': 'application/xml',
                               'Authorization' : 'Basic %s' % base64.encodestring('%s:%s' % (username, password))[:-1]
                      })
                      
    response = urllib2.urlopen(req)
    
    return response.info().getheader('Location')

def get_xml_type(data):
    '''Determines the type of CTS2 XML file by inspecting the first Element'''
    dom = parseString(data)
    
    return dom.childNodes[0].nodeName

def iterate_files(path,action):
    '''Recursively search for CTS2 XML files'''
    if(os.path.isfile(path)):
        action(path)
    else:   
        for root, dirs, files in os.walk(path):
            for name in files:    
                if(name.endswith(".xml")):
                    filename = os.path.join(root, name)
                    action(filename)             
            for sub_dir in dirs:
                iterate_files(sub_dir,action)


def get_create_url(node_name):
    qname = node_name.split(":")
    if(len(qname) == 1):
      return create_urls[qname[0]]
    else:
      return create_urls[qname[1]]

def load(url,user,password,xml_data,changeset,commit):
    '''Loads a CTS2 XML file or set of files
        url: the base URL of the CTS2 Service
        user: user name
        password: password
        xml_data: the File or Directory to load CTS2 XML Files
            NOTE: If this is a Directory, it will be recursively searched
        changeset: the ChangeSetURI to use
            NOTE: If None, a new ChangeSet will be created
        commit: Whether or not to commit the ChangeSet
    ''' 
    if(changeset is None):
        changeset_url = post(url+CHANGE_SET_CREATE,user,password,"")
        changeset = get(url+changeset_url,user,password)
        dom = parseString(changeset)
        change_set_uri = dom.getElementsByTagNameNS(UPDATES_NS, 'ChangeSet')[0].getAttribute('changeSetURI')
        
        print "Created Change Set: " + change_set_uri
        
        changeset = change_set_uri
    
    def process_file(xml_file):
        xml_file = open(xml_file,'r')
        data = xml_file.read()
        data = ''.join([x for x in data if ord(x) < 128])
        xml_file.close()

        xml_type = get_xml_type(data)

        created_url = post(url+get_create_url(xml_type)+"?changesetcontext="+changeset,user,password,data)
        
        print "Created: " + url + '/' + created_url

    iterate_files(xml_data,process_file)
    
    if(commit):
        print "Committing Change Set: " + changeset
        post(url+'/changeset/'+changeset,user,password,COMMIT_CHANGE_SET_XML)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', '-url', help='base CTS2 service URL', required=True)
    parser.add_argument('-d', '--data', help='the directory containing CTS2 XML files', required=True)
    parser.add_argument('-c', '--changeset', help='change set URI', required=False)
    parser.add_argument('-commit', '--commit', help='commit the change set', action='store_true', default=True)
    parser.add_argument('-u', '--user', help='username', required=False)
    parser.add_argument('-p', '--password', help='password', required=False)

    args = parser.parse_args()

    url = args.url
    user = args.user
    password = args.password
    data_directory = args.data
    changeset = args.changeset
    commit = args.commit

    load(url, user, password, data_directory, changeset, commit);
    