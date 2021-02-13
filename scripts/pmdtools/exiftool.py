"""
    Draft: 2020-06-24/MS
"""
from pathlib import Path
import os
import subprocess
import json
import shutil


class Exiftool:
    """Class for embedding and retrieving any metadata
    from a single image file up to all image files in hierarchy of folders"""

    filetypes = (".jpg", ".jpeg", ".tif", ".tiff", ".psd", ".png", ".dng")

    taglist = ()

    grouplist = (
        "XMP-plus:*",
        "XMP-iptcCore:*",
        "XMP-dc:*",
        "IFD0:ImageDescription",
        "IFD0:Artist",
        "IFD0:Copyright",
        "XMP-photoshop:*",
        "XMP-xmpRights:*",
        "IPTC:*")

    opt = " -"
    tagopt = (opt + opt.join(taglist)).split()
    groupopt = (opt + opt.join(grouplist)).split()
    opt = " -ext "
    fnextopt = (opt + opt.join(filetypes)).split()

    def __init__(self, initialoption):
        self._etdata = {}
        self._cmd = "exiftool"
        self._option = initialoption.split()
        self._cmdtags = []
        self._fnextents = self.fnextopt
        self._currentdir = ''
        self.output = ''
        self.error = ''

    @property
    def etdata(self):
        return self._etdata

    @etdata.setter
    def etdata(self, setetdata):
        self._etdata = setetdata

    def embeddata_using_json(self, target):
        """Embedding metadata using metadata in a JSON file as ExifTool parameters"""
        jsonfn = './__tempetdataout.json'
        self.export_as_jsonfile(jsonfn)
        self._option = ('-json=' + jsonfn + " -r -overwrite_original").split()
        resultdata = self.run_cmd(target)
        return resultdata

    def retrievedata(self, source):
        """Retrieving metadata, the data are stored in this class"""
        self._option = ('-j -G1 -struct').split()
        resultcode = self.run_cmd(source)
        return resultcode

    def export_as_jsonfile(self, etjson_fp):
        """Export the metadata of this class to a JSON file"""
        filename = Path(etjson_fp)
        filename = filename.with_suffix('.json')
        with filename.open(mode='w') as _f:
            _f.write(json.dumps(self._etdata, indent=2,
                                ensure_ascii=False, sort_keys=True))

    def import_from_jsonfile(self, etjson_fp):
        """Import ExifTool metadata in a JSON file to this class"""
        if etjson_fp:
            if os.path.isfile(etjson_fp):
                with open(etjson_fp, "r") as etpmdfile:
                    self._etdata = json.load(etpmdfile)

    """
        Below: methods for running exiftool with different commands   
    """

    @property
    def cmd(self):
        return self._cmd

    @cmd.setter
    def cmd(self, et_command):
        # Set the ExifTool command, as required by the operating system
        if et_command != '':
            self._cmd = et_command

    def find_cmd(self):
        self._cmd = shutil.which('exiftool')
        if subprocess._mswindows:
            if self._cmd is None:
                localet_fp = os.path.join(self._currentdir, 'exiftool_windows.exe')
                if os.path.isfile(localet_fp):
                    self._cmd = localet_fp
        else:
            self._cmd = '/usr/local/bin/exiftool'
            if not os.path.exists(self._cmd):
                self._cmd = shutil.which('exiftool')

        if self._cmd is None:
            raise IOError('Executable of ExifTool not available')

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, the_option):
        self._option = the_option.split()

    @property
    def cmdline(self, imagefile):
        """Get the Exif Tool command string"""
        filename = Path(imagefile)
        cmdstr = [self._cmd] + self._option + self._fnextents + self._cmdtags + [filename.name]
        return cmdstr

    @property
    def currentdir(self):
        return self._currentdir

    @currentdir.setter
    def currentdir(self, thecurrentdir):
        if os.path.isdir(thecurrentdir):
            self._currentdir = thecurrentdir

    def run_cmd(self, imagefile):
        """Run the Exif Tool command"""
        self.find_cmd()
        filename = Path(imagefile)
        _rc = None
        if filename.exists():
            cmdstr = [self._cmd] + self._option + self._fnextents + self._cmdtags + [f'{imagefile}']
            etresult = subprocess.run(cmdstr, capture_output=True, check=False)
            _rc = etresult.returncode
            if self._option[0] == '-j':
                self._etdata = json.loads(etresult.stdout)
            self.output = etresult.stdout.decode()
            self.error = etresult.stderr.decode()
        return _rc

    def set_filetype(self, filetypes):
        """Set Exif Tool file types"""
        opt = self.opt
        if len(filetypes) == 0:
            self._fnextents = []
        else:
            self._fnextents = (opt + opt.join(set(filetypes))).split()

    def set_default_filetype(self):
        """Set default file types for Exif Tool"""
        self._fnextents = self.fnextopt

    def __str__(self):
        """Print the Exif Tool command"""
        return ' '.join([self._cmd] + self._option + self._fnextents + self._cmdtags) + "\n"


if __name__ == '__main__':
    MDF = "./myiptcpmd.json"
    IMG = "./images/test-image-1.jpg"

    et = Exiftool('')
    et.set_filetype(['pdf'])
    et.set_default_filetype()
    et.import_from_jsonfile(MDF)
    etresult = et.embeddata_using_json(IMG)
    print(etresult)
    etresult = et.retrievedata(IMG)
    print(etresult)





