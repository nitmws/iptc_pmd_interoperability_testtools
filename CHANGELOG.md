# CHANGELOG of IPTC Photo Metadata Interoperability Test Tools

(latest entry at the top)

* 2021-04-14: IPTC PMD reference switched to new iptc-pmd-techguide.yml. Added investigate... function to ipmdchecker to find out which specified IPTC PMD properties exist in an image file, or not. Added test script investigate_ipmd_props.py.
* 2021-04-06: created ipmdchecker.py with common functions, added compare_prop_values.py to cover Test 2
* 2021-03-24: added explicit encoding='utf8' to writing and reading Exiftool JSON files
* 2021-02-13: initial version, includes only checkfor_missing_props.py to cover Test 3
