"""
    Utilities for mapping identifiers of a standard to codes used by ExifTool
"""
import typing

def minorModelAgeDisclosure_plus2et(plusuri: str) -> str:
    if plusuri == 'http://ns.useplus.org/ldf/vocab/AG-UNK':
        return 'AG-UNK'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-U14':
        return 'AG-U14'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A15':
        return 'AG-A15'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A16':
        return 'AG-A16'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A17':
        return 'AG-A17'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A18':
        return 'AG-A18'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A19':
        return 'AG-A19'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A20':
        return 'AG-A20'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A21':
        return 'AG-A21'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A22':
        return 'AG-A21'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A23':
        return 'AG-A22'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A24':
        return 'AG-A24'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/AG-A25':
        return 'AG-A25'
    else:
        return ''


def minorModelAgeDisclosure_et2plus(etcode: str) -> str:
    if etcode == 'AG-UNK' or etcode == 'AG-U14' or etcode == 'AG-A15' or etcode == 'AG-A16' or etcode == 'AG-A17' or \
            etcode == 'AG-A18' or etcode == 'AG-A19' or etcode == 'AG-A20' or etcode == 'AG-A21' or etcode == 'AG-A22' \
            or etcode == 'AG-A23' or etcode == 'AG-A24' or etcode == 'AG-A25':
        plusURI = 'http://ns.useplus.org/ldf/vocab/' + etcode
        return plusURI
    else:
        return ''


def modelReleaseStatus_plus2et(plusuri: str) -> str:
    if plusuri == 'http://ns.useplus.org/ldf/vocab/MR-NON':
        return 'MR-NON'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/MR-NAP':
        return 'MR-NAP'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/MR-UMR':
        return 'MR-UMR'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/MR-LMR':
        return 'MR-LMR'


def modelReleaseStatus_et2plus(etcode: str) -> str:
    if etcode == 'MR-NON' or etcode == 'MR-NAP' or etcode == 'MR-UMR' or etcode == 'MR-LMR':
        plusuri = 'http://ns.useplus.org/ldf/vocab/' + etcode
        return plusuri
    else:
        return ''


def propertyReleaseStatus_plus2et(plusuri: str) -> str:
    if plusuri == 'http://ns.useplus.org/ldf/vocab/PR-NON':
        return 'PR-NON'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/PR-NAP':
        return 'PR-NAP'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/PR-UPR':
        return 'PR-UPR'
    elif plusuri == 'http://ns.useplus.org/ldf/vocab/PR-LPR':
        return 'PR-LPR'


def propertyReleaseStatus_et2plus(etcode: str) -> str:
    if etcode == 'PR-NON' or etcode == 'PR-NAP' or etcode == 'PR-UPR' or etcode == 'PR-LPR':
        plusuri = 'http://ns.useplus.org/ldf/vocab/' + etcode
        return plusuri
    else:
        return ''

