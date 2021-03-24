"""
Script for matching the exiftool-JSON retrieved from a test image
against a JSON object acting as IPTC Standard reference

"""
import os
import sys
import shutil
import json
import yaml
from pmdtools.exiftool import Exiftool

currentdir = os.path.dirname(os.path.realpath(__file__))

CONFIGFP = currentdir + '/config/scriptsconfig.yml'
with open(CONFIGFP) as yaml_file1:
    scriptconfigs = yaml.safe_load(yaml_file1)

FILESDIR = currentdir + '/' + scriptconfigs['general']['filespathrel']
REFDIR = FILESDIR + 'reference/'
TEST3DIR = FILESDIR + 'test3/'
TESTRESULTSDIR = FILESDIR + 'testresults/'
BACKUP3DIR = FILESDIR + 'backup/test3/'
CACHE3DIR =  FILESDIR + 'cache/test3/'

LOGFP = TESTRESULTSDIR + 'testresults.txt'
IPTCPMDREFFP = REFDIR + 'IPTC-PhotometadataRef-Std2019.1.json'

# load the dictionary with all field/property names as defined by exiftool as key
INVESTIGATIONGUIDEFP = currentdir + '/config/pmdinvestigationguide.yml'
with open(INVESTIGATIONGUIDEFP) as yaml_file1:
    pmdguide = yaml.safe_load(yaml_file1)


def append_line2file(line, filepath):
    with open(filepath, 'a') as textfile:
        textfile.write(line + '\n')


# Exiftool processor
def readpmd_exiftool(imgfp, imgpmd_jsonfp):
    et = Exiftool('')
    et.currentdir = currentdir
    et.retrievedata(imgfp)
    et.export_as_jsonfile(imgpmd_jsonfp)


def get_iptcpropname(etpropname, instructure=False):
    testetpropname = etpropname.replace(":", "_")
    iptcpropname = etpropname
    groupname = 'topwithprefix'
    if instructure:
        groupname = 'instructure'
    if testetpropname in pmdguide[groupname]:
        iptcnameraw = pmdguide[groupname][testetpropname]['label']
        iptcpropname = iptcnameraw.split('|')[0]

    return iptcpropname

def is_registeredpropname(etpropname, instructure=False):
    testetpropname = etpropname.replace(":", "_")
    iptcpropname = etpropname
    groupname = 'topwithprefix'
    if instructure:
        groupname = 'instructure'
    isreg = False
    if testetpropname in pmdguide[groupname]:
        isreg = True
    return isreg

def check_pmdstructure(parent_propnames, refstru, teststru, testresultsfp):
    for propname in refstru:
        if not is_registeredpropname(propname, True):
            continue
        iptcname = get_iptcpropname(propname, True)
        iptcnames = parent_propnames + '->' + iptcname
        if propname in teststru:
            propval = refstru[propname]
            # if the prop has a singular cardinality the value is a dict, if multi-cardinality the value is a list
            if isinstance(propval, dict):
                check_pmdstructure(iptcnames, refstru[propname], teststru[propname], testresultsfp)
            if isinstance(propval, list):
                # special: as all structures of the reference dict are complete it is sufficient to use the first one
                refobj = propval[0]
                if isinstance(refobj, dict):  # check only if a dict, all other types are not relevant
                    listindex = 1
                    for testobj in teststru[propname]:
                        check_pmdstructure(iptcnames + '[' + str(listindex) + ']', refobj, testobj, testresultsfp)
                        listindex += 1
        else:
            msg = 'MISSING property: {}'.format(iptcnames)
            print(msg)
            append_line2file(msg, LOGFP)
            append_line2file(msg, testresultsfp)

def check_mainpmd(test_json_fp, testresultsfp):

    with open(IPTCPMDREFFP, encoding='utf-8') as refjson_file:
        ipmdref = json.load(refjson_file)[0]

    with open(test_json_fp, encoding='utf-8') as testjson_file:
        ipmdtest = json.load(testjson_file)[0]

    if 'File:Comment' in ipmdtest:
        msg = "COMMENT in the file: " + ipmdtest['File:Comment']
        print(msg)
        append_line2file(msg, LOGFP)
        append_line2file(msg, testresultsfp)

    for propname in ipmdref:
        if not is_registeredpropname(propname):
            continue
        iptcname = get_iptcpropname(propname)
        if propname in ipmdtest:
            propval = ipmdref[propname]
            # if the key has a singular cardinality the value is a dict, if multi-cardinality the value is a list
            if isinstance(propval, dict):
                check_pmdstructure(iptcname, ipmdref[propname], ipmdtest[propname], testresultsfp)
            if isinstance(propval, list):
                # special: as all structures of the reference dict are complete it is sufficient to use the first one
                refobj = propval[0]
                if isinstance(refobj, dict):  # check only if a dict, all other types are not relevant
                    listindex = 1
                    for testobj in ipmdtest[propname]:
                        check_pmdstructure(iptcname + '[' + str(listindex) + ']', refobj, testobj, testresultsfp)
                        listindex += 1
        else:
            msg = 'MISSING property: {}'.format(iptcname)
            print(msg)
            append_line2file(msg, LOGFP)
            append_line2file(msg, testresultsfp)

def find_test3files(testdirpath):
    foundfn = []
    for fn in os.listdir(testdirpath):
        if fn.endswith('.jpg'):
            foundfn.append(fn)
        if fn.endswith('.png'):
            foundfn.append(fn)
    return foundfn


def run_test3(testimgfn):
    coretestimgfn = os.path.splitext(testimgfn)[0]
    testimgfp = TEST3DIR + testimgfn
    testjsonfp = CACHE3DIR + coretestimgfn + '.json'
    testresults1fp = TESTRESULTSDIR + coretestimgfn + '.txt'
    backupimgfp = BACKUP3DIR + testimgfn

    readpmd_exiftool(testimgfp,testjsonfp)
    if os.path.isfile(testjsonfp):
        msg = 'Tested(3) JSON file of image: ' + testimgfn
        print(msg)
        append_line2file(msg, LOGFP)
        check_mainpmd(testjsonfp, testresults1fp)
        append_line2file('***** TEST FINISHED *****', testresults1fp)
        shutil.move(testimgfp, backupimgfp)
    else:
        print('No JSON file generated by ExifTool for ' + testjsonfp)




def dummy00():
    testfp = './testdata/ipmd_testsource02.json'
    append_line2file('Tested JSON file: ' + testfp, LOGFP)
    check_mainpmd(testfp)

### MAIN

foundtest3images = find_test3files(TEST3DIR)

print(foundtest3images)

for testimgfn in foundtest3images:
    run_test3(testimgfn)
