# sample files

Explains the config of all sample files.

All sample files must be copied, renamed and edited to fit your needs.

## 1 settings.sample.json

This file contains the basic settings for the app.

- **Location**: [/pytia_bill_of_material/resources/settings.sample.json](../pytia_bill_of_material/resources/settings.sample.json)
- **Rename to**: `settings.json`

### 1.1 file content

```json
{
    "title": "PYTIA Bill Of Material",
    "debug": false,
    "export": {
        "apply_username_in_bom": true,
        "apply_username_in_docket": true
    },
    "restrictions": {
        "allow_all_users": false,
        "allow_all_editors": false,
        "allow_unsaved": false,
        "allow_outside_workspace": true,
        "strict_project": true,
        "enable_information": true
    },
    "paths": {
        "catia": "C:\\CATIA\\V5-6R2017\\B27",
        "local_dependencies": "C:\\pytia\\local_deps",
        "release": "C:\\pytia\\release"
    },
    "files": {
        "bom_export": "Bill of Material.xlsx",
        "app": "pytia_bill_of_material.pyz",
        "launcher": "pytia_bill_of_material.catvbs",
        "workspace": "workspace.yml"
    },
    "urls": {
        "help": "https://github.com/deloarts/pytia-bill-of-material"
    },
    "mails": {
        "admin": "admin@company.com"
    }
}
```

### 1.2 description

name | type | description
--- | --- | ---
title | `str` | The apps title. This will be visible in the title bar of the window.
debug | `bool` | The flag to declare the debug-state of the app. The app cannot be built if this value is true.
restrictions.allow_all_users | `bool` | If set to `true` any user can make changes to the documents properties. If set to `false` only those users from the **users.json** file can modify the properties.
restrictions.allow_all_editors | `bool` | If set to `true` any user can make changes to the documents properties. If set to `false` only those users which are declared in the **workspace** file can modify the properties. If no workspace file is found, or no **editors** list-item is inside the workspace file, then this is omitted, and everyone can make changes.
restrictions.allow_unsaved | `bool` | If set to `false` an unsaved document (a document which doesn't have a path yet) cannot be modified.
restrictions.allow_outside_workspace | `bool` | If set to `false` a **workspace** file must be provided somewhere in the folder structure where the document is saved. This also means, that an unsaved document (a document which doesn't have a path yet) cannot be modified.
restrictions.strict_project | `bool` | If set to `true` the project number must be present in the **workspace** file, otherwise the changes to the properties cannot be saved. If no workspace file is found, or no **projects** list-item is inside the workspace file, then this is omitted, and any project number can be written to the documents properties.
restrictions.enable_information | `bool` | If set to `true` the user will see the notifications from the **information.json** file.
paths.catia | `str` | The absolute path to the CATIA executables.
paths.local_dependencies | `str` | The folder where local local_dependencies (python wheel files) for the installer are stored.
paths.release | `str` | The folder where the launcher and the app are released into.
file.bom_export | `str` | The standard name for the final bill of material. If a bom_name is set in the **workspace** file, the workspace-bom-name will be used.
files.app | `str` | The name of the released python app file.
files.launcher | `str` | The name of the release catvbs launcher file.
files.workspace | `str` | The name of the workspace file.
urls.help | `str` or `null` | The help page for the app. If set to null the user will receive a message, that no help page is provided.
mails.admin | `str` | The mail address of the sys admin. Required for error mails.

## 2 users.sample.json

This file contains a list of users known to the system.

- **Location**: [/pytia_bill_of_material/resources/users.sample.json](../pytia_bill_of_material/resources/users.sample.json)
- **Rename to**: `users.json`

### 2.1 file content

```json
[
    {
        "logon": "admin",
        "id": "001",
        "name": "Administrator",
        "mail": "admin@company.com"
    },
    ...
]
```

### 2.2 description

name | type | description
--- | --- | ---
logon | `str` | The windows logon name of the user.
id | `str` | The ID of the user. Can be used for the employee ID.
name | `str` | The name of the user.
mail | `str` | The users mail address.

## 3 docket.sample.json

This file contains the configuration for the docket export.

> ⚠️ This config file will be documented later, as the docket generation will be changed in the future (it's currently a very hacky solution).

- **Location**: [/pytia_bill_of_material/resources/docket.sample.json](../pytia_bill_of_material/resources/users.sample.json)
- **Rename to**: `docket.json`
