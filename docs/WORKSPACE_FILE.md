# workspace file

Explains the config of the workspace yaml files.

## 1 file content

```yaml
title: "An important project"
active: true
customer: "Cat"
description: "Lorem ipsum"
machine: "M00001"
projects:
  - "P12345"
  - "P23456"
  - "P34567"
responsible: "Dr. Awkward"
delegate: "Mr. Alarm"
editors:
  - "Employee 1"
  - "Employee 2"
```

## 2 description

> All items of the workspace file are optional. You can either leave the values empty, remove the key completely or comment it out by using the hash `#` symbol.

name | type | description
--- | --- | ---
title | `str` | The title of the project/workspace.
active | `bool` | Defines the state of the project. If set to `false` nobody can write changes to the part properties.
customer | `str` | The name of the customer of the project.
description | `str` | The description of the project.
machine | `str` | The machine number, in which the part is assembled.
projects | `List[str]` or `str` | The list of projects associated with this machine/workspace.
responsible | `str` | The name of the person that is responsible for the project.
delegate | `str` | The name of the person that is representative for the responsible person.
editors | `List[str]` or `str` | The list of editors that are allowed to make changes to the part properties. If the value of the **settings.json** key `restrictions.allow_all_editors` is set to `false`, only those editors are allowed to make changes to the part properties. If set to `true`, the editors list will be ignored.

## 3 example file

This example file is with comments, so any person involved in this project can edit the file easily.

```yaml
# This is the workspace file. Edit this file to fit the purpose of the machine.
# All keys are optional, you can either delete them, remove the values or comment
# them out, by using the hash '#' symbol.

# Important: This workspace file alters the behavior of all PYTIA apps, be very
# careful when editing this file.

# The title of the workspace. Any text is valid.
title: "An important project"

# The state of the workspace. Possible values are `true` and `false`.
# If the state is `false`, no one can make changes to CATIA properties.
active: true

# The customer name. Any text is valid.
customer: "Cat"

# The description. Any text is valid.
description: "Lorem ipsum"

# The unique machine identification number. Any text is valid, but it should be
# unique among all machine.
machine: "M00001"

# The project numbers, that are associated with this machine. This can either be
# a list or values, or a single value.
projects:
  - "P12345"
  - "P23456"
  - "P34567"

# The responsible person for this machine.
responsible: "Dr. Awkward"

# The representative of the responsible person for this machine.
delegate: "Mr. Alarm"

# The list of editors, that are allowed to make changes to CATIA properties via
# the PYTIA apps. If this list is omitted, everyone is allowed to make changes
# via the PYTIA apps.
# The values of this key are associated with the Windows logon name (the username
# in the domain).
editors:
  - "Employee 1"
  - "Employee 2"
```
