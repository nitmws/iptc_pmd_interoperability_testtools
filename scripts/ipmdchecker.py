"""
Script doing the "check IPTC Photo Metadata" jobs and providing some shared functions
"""
import os
import yaml
import json
from pmdtools.exiftool import Exiftool

currentdir = os.path.dirname(os.path.realpath(__file__))

CONFIGFP = currentdir + '/config/scriptsconfig.yml'
with open(CONFIGFP) as yaml_file1:
    scriptconfigs = yaml.safe_load(yaml_file1)

# load the dictionary with all field/property names as defined by exiftool as key
INVESTIGATIONGUIDEFP = currentdir + '/config/pmdinvestigationguide.yml'
with open(INVESTIGATIONGUIDEFP) as yaml_file1:
    pmdguide = yaml.safe_load(yaml_file1)

FILESDIR = currentdir + '/' + scriptconfigs['general']['filespathrel']
REFDIR = FILESDIR + 'reference/'
IPTCPMDREFFP = REFDIR + 'IPTC-PhotometadataRef-Std2019.1.json'

TESTRESULTSDIR = FILESDIR + 'testresults/'
LOGFP = TESTRESULTSDIR + 'testresults_all.txt'


def append_line2file(line: str, filepath: str) -> None:
    """Appends a line to a text file

    :param line: line of text
    :param filepath: path of the text file
    :return: nothing
    """
    with open(filepath, 'a') as textfile:
        textfile.write(line + '\n')


def readpmd_exiftool(imgfp: str, imgpmd_jsonfp: str) -> None:
    """ExifTool reads photo metadata out of an image file and writes it to a JSON file

    :param imgfp: path of the image file
    :param imgpmd_jsonfp: path of the JSON file
    :return: nothing
    """
    et = Exiftool('')
    et.currentdir = currentdir
    et.retrievedata(imgfp)
    et.export_as_jsonfile(imgpmd_jsonfp)


def find_testfiles(testdirpath: str) -> list:
    """ Collects a list of file names in a folder

    :param testdirpath: path of the to-be-investigated directory
    :return: list of file names
    """
    foundfn = []
    for fn in os.listdir(testdirpath):
        if fn.endswith('.jpg'):
            foundfn.append(fn)
        if fn.endswith('.png'):
            foundfn.append(fn)
    return foundfn


def get_iptcpropname(etpropname: str, instructure: bool = False) -> str:
    """Gets the IPTC Photo Metadata property name corresponding to
    the name of an ExifTool tag

    :param etpropname: ExifTool tag
    :param instructure: True if the property is one of an IPTC PMD structure
    :return: IPTC property name
    """
    testetpropname = etpropname.replace(":", "_")
    iptcpropname = etpropname
    groupname = 'topwithprefix'
    if instructure:
        groupname = 'instructure'
    if testetpropname in pmdguide[groupname]:
        iptcnameraw = pmdguide[groupname][testetpropname]['label']
        iptcpropname = iptcnameraw.split('|')[0]
    return iptcpropname


def is_iptcpmdpropname(etpropname: str, instructure: bool = False) -> bool:
    """Checks if the ExifTool tag name corresponds to a specified
    IPTC Photo Metadata property

    :param etpropname:
    :param instructure:
    :return:
    """
    testetpropname = etpropname.replace(":", "_")
    groupname = 'topwithprefix'
    if instructure:
        groupname = 'instructure'
    isspecified: bool = False
    if testetpropname in pmdguide[groupname]:
        isspecified = True
    return isspecified


def check_pmdstructure(parent_propnames: str, refstru: dict, teststru: dict,
                       testresultsfp: str, comparevalues: bool = False) -> None:
    """Checks an IPTC Photo Metadata structure at any level below the top level.

    :param parent_propnames: a sequence of names of parent properties
    :param refstru: reference structure of the IPTC Photo Metadata
    :param teststru: test structure of the test image
    :param testresultsfp: path of the file for logging test results
    :param comparevalues: False: only missing properties are reported, True: changed property values too
    :return: nothing
    """
    for refpropname in refstru:
        if not is_iptcpmdpropname(refpropname, True):
            continue
        iptcname = get_iptcpropname(refpropname, True)
        iptcnames = parent_propnames + '->' + iptcname
        if refpropname in teststru:
            refpropval = refstru[refpropname]
            # do the checking differently for dict, list and plain value types
            if isinstance(refpropval, dict):
                check_pmdstructure(iptcnames, refstru[refpropname], teststru[refpropname], testresultsfp, comparevalues)
            if isinstance(refpropval, list):
                if comparevalues:
                    idx = 0
                    while idx < len(refpropval):  # iterate across the items of the list
                        refpropval2 = refstru[refpropname][idx]
                        testpropval2 = teststru[refpropname][idx]
                        idx += 1
                        if isinstance(refpropval2, str) or isinstance(refpropval2, int) or \
                                isinstance(refpropval2, float):
                            # compare only plain values, not a list or dict
                            if testpropval2 != refpropval2:
                                msg = f'CHANGED value of property <{iptcname}> is: {testpropval2}'
                                print(msg)
                                append_line2file(msg, LOGFP)
                                append_line2file(msg, testresultsfp)
                idx = 0
                while idx < len(refpropval):
                    refobj = refpropval[idx]
                    if isinstance(refobj, dict):  # check only if a dict, all other types are not relevant
                        testobj = teststru[refpropname][idx]
                        check_pmdstructure(iptcnames + '[' + str(idx) + ']', refobj, testobj,
                                           testresultsfp, comparevalues)
                    idx += 1
            if comparevalues:
                if isinstance(refpropval, str) or isinstance(refpropval, int) or isinstance(refpropval, float):
                    # the value is a plain one = compare the values
                    testpropval = teststru[refpropname]
                    if testpropval != refpropval:
                        msg = f'CHANGED value of property <{iptcnames}> is: {testpropval}'
                        print(msg)
                        append_line2file(msg, LOGFP)
                        append_line2file(msg, testresultsfp)
        else:
            msg = f'MISSING property: {iptcnames}'
            print(msg)
            append_line2file(msg, LOGFP)
            append_line2file(msg, testresultsfp)


def check_mainpmd(test_json_fp: str, testresultsfp: str, comparevalues: bool = False) -> None:
    """Checks IPTC Photo Metadata at the top level (=properties not inside a structure)

    :param test_json_fp: path of the JSON file with metadata retrieved from the image file by ExifTool
    :param testresultsfp: path of the file for logging test results
    :param comparevalues: False: only missing properties are reported, True: changed property values too
    :return:
    """
    with open(IPTCPMDREFFP, encoding='utf-8') as refjson_file:
        ipmdref = json.load(refjson_file)[0]

    with open(test_json_fp, encoding='utf-8') as testjson_file:
        ipmdtest = json.load(testjson_file)[0]

    if 'File:Comment' in ipmdtest:
        msg = f"COMMENT in the file: {ipmdtest['File:Comment']}"
        print(msg)
        append_line2file(msg, LOGFP)
        append_line2file(msg, testresultsfp)

    for refpropname in ipmdref:
        if not is_iptcpmdpropname(refpropname):
            continue
        iptcname = get_iptcpropname(refpropname)
        if refpropname in ipmdtest:
            refpropval = ipmdref[refpropname]
            # do the checking differently for dict, list and plain value types
            if isinstance(refpropval, dict):
                check_pmdstructure(iptcname, ipmdref[refpropname], ipmdtest[refpropname], testresultsfp, comparevalues)
            if isinstance(refpropval, list):
                if comparevalues:
                    idx = 0
                    while idx < len(refpropval):  # iterate across the items of the list
                        refpropval2 = ipmdref[refpropname][idx]
                        testpropval2 = ipmdtest[refpropname][idx]
                        idx += 1
                        if isinstance(refpropval2, str) or isinstance(refpropval2, int) or \
                                isinstance(refpropval2, float):
                            # compare only plain values, not a list or dict
                            if testpropval2 != refpropval2:
                                msg = f'CHANGED value of property <{iptcname}> is: {testpropval2}'
                                print(msg)
                                append_line2file(msg, LOGFP)
                                append_line2file(msg, testresultsfp)
                idx = 0
                while idx < len(refpropval):
                    refobj = refpropval[idx]
                    if isinstance(refobj, dict):  # check only if a dict, all other types are not relevant
                        testobj = ipmdtest[refpropname][idx]
                        check_pmdstructure(iptcname + '[' + str(idx) + ']', refobj, testobj,
                                           testresultsfp, comparevalues)
                    idx += 1
            if comparevalues:
                if isinstance(refpropval, str) or isinstance(refpropval, int) or isinstance(refpropval, float):
                    # the value is a plain one = compare the values
                    testpropval = ipmdtest[refpropname]
                    if testpropval != refpropval:
                        msg = f'CHANGED value of property <{iptcname}> is: {testpropval}'
                        print(msg)
                        append_line2file(msg, LOGFP)
                        append_line2file(msg, testresultsfp)
        else:
            msg = f'MISSING property: {iptcname}'
            print(msg)
            append_line2file(msg, LOGFP)
            append_line2file(msg, testresultsfp)
