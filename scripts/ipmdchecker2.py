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
IPMDTECHGUIDEFP = currentdir + '/config/iptc-pmd-techguide.yml'
with open(IPMDTECHGUIDEFP) as yaml_file1:
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
    groupname = 'et_topwithprefix'
    if instructure:
        groupname = 'et_instructure'
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
    groupname = 'et_topwithprefix'
    if instructure:
        groupname = 'et_instructure'
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
    :return: nothing
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


def investigate_ipmdstructure(parent_propnames: str, ugtopic: str, parent_so: str, level: int,
                              structid: str, teststruct: dict,
                              testresults_text_fp: str, testresults_csv_fp: str,
                              csvsep: str = ',') -> None:
    """Investigates which IPTC Photo Metadata properties exist inside a structure.
    This function may be called recursively. Only investigations at level 2 and 3 are supported (currently).

    :param parent_propnames: names/labels of parent properties, csvsep-separated
    :param ugtopic: IPTC User Guide topic of the top level property
    :param parent_so: sort order of the parent property
    :param level: level of the investigation. Top level = level 1
    :param structid: IPTC PMD identifier of the investigated structure
    :param teststruct: structure (dict) from the tested image file
    :param testresults_text_fp: path of the file for logging test results
    :param testresults_csv_fp: path of the CSV file for logging test results
    :return: nothing
    """
    if level < 2 or level > 3:
        return

    groupname = 'ipmd_struct'
    if structid in pmdguide[groupname]:
        refstru = pmdguide[groupname][structid]
    else:
        return
    for ipmdpropid in refstru:
        ipmdprop: dict = refstru[ipmdpropid]
        if 'label' in ipmdprop:
            label: str = ipmdprop['label']
        else:
            label: str = 'UNKNOWN-ERROR'
        msg: str = f'*** Investigating IPTC PMD structure <{label} used by {parent_propnames}>'
        print(msg)
        csvrow: str = ugtopic + csvsep
        if 'sortorder' in ipmdprop:
            sortorder: str = ipmdprop['sortorder']
        else:
            sortorder: str = 'xxx'
        csvrow += parent_so + '-' + sortorder + csvsep
        datatype: str = 'xxx'
        if 'datatype' in ipmdprop:
            datatype: str = ipmdprop['datatype']
        dataformat: str = ''
        if 'dataformat' in ipmdprop:
            dataformat: str = ipmdprop['dataformat']
        invstructid: str = ''  # id/name of a structure to be investigated
        if datatype == 'struct':
            if dataformat == 'AltLang':  # workaround to cover what ExifTool returns for AltLang values: a string
                datatype = 'string'
            else:
                invstructid = dataformat

        if level == 2:
            csvrow += parent_propnames + csvsep + label + csvsep + 'x' + csvsep  # NameL1 inherited, L2 applied, L3 x-ed
        if level == 3:
            csvrow += parent_propnames + csvsep + label + csvsep  # NameL1 inherited, L2 applied, L3 x-ed
        csvrow += 'not spec' + csvsep  # = the IIM column
        xmpvalue = ''
        if 'etTag' in ipmdprop:
            ettag = ipmdprop['etTag']
            if isinstance(teststruct, list):
                propfound: bool = False
                for singleteststru in teststruct:
                    if ettag in singleteststru:
                        propfound = True
                if propfound:
                    keymsg = 'found'
                else:
                    keymsg = 'MISSING'
            else:
                if ettag in teststruct:
                    keymsg = 'found'
                    xmpvalue = teststruct[ettag]
                else:
                    keymsg = 'MISSING'
            msg = f'{keymsg} its corresponding XMP property'
            print(msg)
            append_line2file(msg, testresults_text_fp)
            csvrow += keymsg + csvsep # = the XMP column
        else:
            csvrow += 'not spec' + csvsep
        csvrow += '---' + csvsep
        append_line2file(csvrow, testresults_csv_fp)
        if invstructid != '':
            investigate_ipmdstructure(parent_propnames + csvsep + label, ugtopic, parent_so + '-' + sortorder,
                                      level + 1, invstructid, xmpvalue,
                                      testresults_text_fp, testresults_csv_fp, csvsep)


def investigate_mainpmd(test_json_fp: str, testresults_text_fp: str, testresults_csv_fp: str,
                        csvsep: str = ',') -> None:
    """Investigates which IPTC Photo Metadata top level (=properties not inside a structure) properties exist

    :param test_json_fp: path of the JSON file with metadata retrieved from the image file by ExifTool
    :param testresults_text_fp: path of the file for logging test results
    :param testresults_csv_fp: path of the CSV file for logging test results
    :return: nothing
    """
    with open(test_json_fp, encoding='utf-8') as testjson_file:
        ipmdtest = json.load(testjson_file)[0]

    csvheader: str = f'topic{csvsep}sortorder{csvsep}IPMD Name L1{csvsep}IPMD Name L2{csvsep}IPMD Name L3'
    csvheader += f'{csvsep}IIM prop{csvsep}XMP prop{csvsep}Sync Values{csvsep}Comments'
    append_line2file(csvheader, testresults_csv_fp)
    groupname = 'ipmd_top'
    for ipmdpropid in pmdguide[groupname]:
        ipmdprop: dict = pmdguide[groupname][ipmdpropid]
        if 'label' in ipmdprop:
            label: str = ipmdprop['label']
        else:
            label: str = 'UNKNOWN-ERROR'
        msg: str = f'*** Investigating IPTC PMD property <{label}>'
        print(msg)
        append_line2file(msg, testresults_text_fp)
        if 'ugtopic' in ipmdprop:
            ugtopic: str = ipmdprop['ugtopic']
        else:
            ugtopic: str = 'xxx'
        csvrow: str = ugtopic + csvsep
        if 'sortorder' in ipmdprop:
            sortorder: str = ipmdprop['sortorder']
        else:
            sortorder: str = 'xxx'
        csvrow += sortorder + csvsep
        csvrow += label + csvsep + 'x' + csvsep + 'x' + csvsep  # Name L1 is set, L2 and L3 x-ed out
        datatype: str = 'xxx'
        if 'datatype' in ipmdprop:
            datatype: str = ipmdprop['datatype']
        dataformat: str = ''
        if 'dataformat' in ipmdprop:
            dataformat: str = ipmdprop['dataformat']
        invstructid: str = ''  # id/name of a structure to be investigated
        if datatype == 'struct':
            if dataformat == 'AltLang':  # workaround to cover what ExifTool returns for AltLang values: a string
                datatype = 'string'
            else:
                invstructid = dataformat
        plainvalue: bool = False
        if datatype == 'string' or datatype == 'number':
            plainvalue = True

        iimfound: bool = False
        iimvalue: str = ''
        xmpvalue = ''

        special_comparing: str = ''  # indicated a special procedure for comparing values
        if ipmdpropid == 'creatorNames':
            special_comparing += 'iim1xmplist|'
        if ipmdpropid == 'dateCreated':
            special_comparing += 'iimdatetime|'

        if 'etIIM' in ipmdprop:
            ettag = ipmdprop['etIIM']
            if ettag in ipmdtest:
                keymsg = 'found'
                iimfound = True
                if plainvalue:
                    iimvalue = ipmdtest[ettag]
            else:
                keymsg = 'MISSING'
            if ettag == 'IPTC:DateCreated+IPTC:TimeCreated':
                keymsg = 'MISSING'
                if 'IPTC:DateCreated' in ipmdtest and 'IPTC:TimeCreated' in ipmdtest:
                    keymsg = 'found'
            msg = f'{keymsg} its corresponding IIM property'
            print(msg)
            append_line2file(msg, testresults_text_fp)
            csvrow += keymsg + csvsep
        else:
            csvrow += 'not spec' + csvsep
        if 'etXMP' in ipmdprop:
            ettag = ipmdprop['etXMP']
            if ettag in ipmdtest:
                keymsg = 'found'
                xmpvalue = ipmdtest[ettag]
            else:
                keymsg = 'MISSING'
            msg = f'{keymsg} its corresponding XMP property'
            print(msg)
            append_line2file(msg, testresults_text_fp)
            csvrow += keymsg + csvsep
        else:
            csvrow += 'not spec' + csvsep
        keymsg = '---'
        # compare plain values
        if plainvalue:
            if iimfound:
                if iimvalue == xmpvalue:
                    keymsg = 'in sync'
                else:
                    keymsg = 'NOT SYNC'
                if 'iim1xmplist' in special_comparing:  # it may override the keymsg above!
                    if isinstance(xmpvalue, list):
                        if len(xmpvalue) > 0:
                            if iimvalue == xmpvalue[0]:
                                keymsg = 'in sync'
                            else:
                                keymsg = 'NOT SYNC'

            if 'iimdatetime' in special_comparing:  # it may override the keymsg above!
                iimdatevalue: str = ''
                dateettag: str = 'IPTC:DateCreated'
                if dateettag in ipmdtest:
                    iimdatevalue = ipmdtest[dateettag]
                iimtimevalue: str = ''
                timeettag: str = 'IPTC:TimeCreated'
                if timeettag in ipmdtest:
                    iimtimevalue = ipmdtest[timeettag]
                iimdatetimevalue = iimdatevalue + ' ' + iimtimevalue
                if iimdatetimevalue == xmpvalue:
                    keymsg = 'in sync'
                else:
                    keymsg = 'NOT SYNC'



        csvrow += keymsg + csvsep
        append_line2file(csvrow, testresults_csv_fp)
        if invstructid != '':
            investigate_ipmdstructure(label, ugtopic, sortorder, 2, invstructid, xmpvalue,
                                      testresults_text_fp, testresults_csv_fp, csvsep)



