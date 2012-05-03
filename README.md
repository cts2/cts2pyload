### cts2pyload
A utility to load CTS2 XML files into a CTS2 service that supports the Maintenance Profile.

### Usage
```
usage: cts2pyload.py [-h] -url URL -d DATA [-c CHANGESET] [-commit] [-u USER]
                     [-p PASSWORD]

arguments:
  -h, --help            show this help message and exit
  -url URL, -url URL    base CTS2 service URL
  -d DATA, --data DATA  the directory containing CTS2 XML files
  -c CHANGESET, --changeset CHANGESET
                        change set URI
  -commit, --commit     commit the change set
  -u USER, --user USER  username
  -p PASSWORD, --password PASSWORD
                        password
```

### Notes
* If no 'changeset' parameters is included, a new ChangeSet will be opened and (optionally) committed.
* The specified 'data' directory will be recursively scanned for any '*.xml' file.
* Any valid CTS2 Resource XML file is allowed:
 	  CodeSystemCatalogEntry
      CodeSystemVersionCatalogEntry
      ValueSetCatalogEntry
      ValueSetDefinition
      ResolvedValueSet
      EntityDescription
      MapCatalogEntry
      MapVersion
      MapEntry
      ConceptDomainCatalogEntry
      ConceptDomainBinding
      Association
