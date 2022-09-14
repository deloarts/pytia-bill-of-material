# pytia bill of material

A python app for exporting the bill of material from a CATIA V5 product.

![state](https://img.shields.io/badge/State-Alpha-brown.svg?style=for-the-badge)
![version](https://img.shields.io/badge/Version-0.3.1-orange.svg?style=for-the-badge)

[![python](https://img.shields.io/badge/Python-3.10-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
![catia](https://img.shields.io/badge/CATIA-V5%206R2017-blue.svg?style=for-the-badge)
![OS](https://img.shields.io/badge/OS-WIN10%20|%20WIN11-blue.svg?style=for-the-badge)

> ⚠️ The layout of this app is heavily biased towards the workflow and needs of my companies' engineering team. Although almost everything can be changed via config files and presets, the apps basic functionality is built to work in the environment of said company.

Check out the pytia ecosystem:

- [pytia](https://github.com/deloarts/pytia): The heart of this project.
- [pytia-property-manager](https://github.com/deloarts/pytia-property-manager): An app to edit part and product properties.
- [pytia-bounding-box](https://github.com/deloarts/pytia-bounding-box): An app to retrieve the bounding box of a part.
- [pytia-bill-of-material](https://github.com/deloarts/pytia-bill-of-material): An app to retrieve the bill of material of a product.
- [pytia-title-block](https://github.com/deloarts/pytia-title-block): An app to edit a drawing's title block.
- [pytia-ui-tools](https://github.com/deloarts/pytia-ui-tools): A toolbox for all pytia apps.

## 1 installation

### 1.1 user

On the users machine you need to install the following:

- CATIA
- [Python](https://www.python.org/downloads/)

When the user starts the app it will automatically install all its requirements. Further the app also updates outdated dependencies if needed. The apps environment will be created in the users appdata-folder: `C:\Users\User\AppData\Roaming\pytia\pytia_bill_of_material`

Recommended python install options for the user:

```powershell
python-installer.exe /passive PrependPath=1 Include_doc=0 Include_test=0 SimpleInstall=1 SimpleInstallDescription="python for pytia"
```

For convenience there is a powershell script that will install the required python version for you, see [assets/python_installer.ps1](assets/python_installer.ps1).

### 1.2 developer

On the developers machine (this is you) install the following:

- CATIA
- [Python](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/master/)

> ✏️ Use poetry to install all dependencies and dev-dependencies to work on this project.
>
> 🔒 Some dependencies are from private repos. You need to have [ssh-access](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) to those repositories. Test your ssh connection with `ssh -T git@github.com`
>
> ❗️ Never develop new features and fixes in the main branch!

## 2 setup

### 2.1 resource files

All configuration is done via json files inside the [resources folder](/pytia_bill_of_material/resources/).

#### 2.1.1 default files

You can leave the default configuration if it suits your needs, but you can always copy any default json file, rename (get rid of 'default') it and edit its content.

Example: If you want to change the content of the [filters.default.json](/pytia_bill_of_material/resources/filters.default.json) you have to copy this file, and paste it as **filters.json**. Then you can edit the content of your newly generated filters-settings file. Same for any other default-resource file.

> ✏️ For a full description of all default files, see [docs/DEFAULT_FILES.md](/docs/DEFAULT_FILES.md).

#### 2.1.2 sample files

Files that are named like **settings.sample.json** must be copied, renamed and edited. Sample files exists only for you to have a guide, of how the config file must look.

Example: Before you can build the app you have to copy the [settings.sample.json](/pytia_bill_of_material/resources/settings.sample.json) and rename it to **settings.json**. Then you can edit its content to match your requirements.

> ✏️ For a full description of all sample files, see [docs/SAMPLE_FILES.md](/docs/SAMPLE_FILES.md).

#### 2.1.3 static files

Files without 'default' or 'sample' in their names cannot be changed! Just leave them there, they are needed for the app to work.

### 2.2 template files

The app uses optional template files, see [templates folder](/pytia_bill_of_material/templates/). To use a template file, copy it and remove the `sample` from the name.

If you want to use the docket-generation-feature you have to add a `docket.CATDrawing` CATIA file in this folder. There is already a sample file in this folder, which is ready-to-use with the [docket.sample.json](/pytia_bill_of_material/resources/docket.sample.json) config file -> rename both files to `docket.CATDrawing` and `docket.json` and the docket generation will work, tweak both files to fit your needs.

### 2.3 provide local dependencies

Some dependencies are not publicly available on PyPi or GitHub (because they are private). Therefore it's necessary to provide the wheel-file locally for the app to auto-install it. The list below shows said local deps:

Name | Link | Version
--- | --- | ---
**pytia** | <https://github.com/deloarts/pytia> | [0.2.2](https://github.com/deloarts/pytia/releases/tag/v0.2.2)
**pytia-ui-tools** | <https://github.com/deloarts/pytia-ui-tools> | [0.5.3](https://github.com/deloarts/pytia-ui-tools/releases/tag/v0.5.3)

> ❗️ The folder where you provide the local dependencies must match the **paths.local_dependencies** entry of the **settings.json**. The user must have at least read access on this folder.
>
> ✏️ Put the wheel file on a shared network drive if you have multiple users.

### 2.4 provide a release folder

To be able to launch the app from within CATIA you need to provide a release folder, where the app and a launcher file are stored. Both files (the app and the launcher) will be created with the [_build.py](_build.py) script, and released to the release-folder with the [_release.py](_release.py) script.

> ❗️ Add this release folder to the **settings.json** file as value of the **paths.release** key.

### 2.5 test

Most tests require CATIA running. Test suite is pytest. For testing with poetry run:

```powershell
poetry run pytest
```

> ⚠️ Test discovery in VS Code only works when CATIA is running.

### 2.6 build

> ❗️ Do not build the app with poetry! This package is not not meant to be used as an import, it should be used as an app.

To build the app and make it executable for the user run the [_build.py](_build.py) python file. The app is only built if all tests are passing. The app will be exported to the [_build-folder](/build/). Additionally to the built python-file a catvbs-file will be exported to the same build-folder. This file is required to launch the app from within CATIA, see the next chapter.

> ✏️ You can always change the name of the build by editing the value from the **files.app** key of the **settings.json**.
>
> ✏️ The reason this app isn't compiled to an exe is performance. It takes way too long to load the UI if the app isn't launched as python zipfile.

### 2.7 release

To release the app into the provided release folder run the [_release.py](_release.py) script.

To run the app from within CATIA, add the release-folder to the macro-library in CATIA. CATIA will recognize the catvbs-file, so you can add it to a toolbar.

You can always change the path of the release folder by editing the value from the **paths.release** key of the **settings.json**.

> ⚠️ Once you built and released the app you cannot move the python app nor the catvbs script to another location, because absolute paths will be written to those files. If you have to move the location of the files you have to change the paths in the **settings.json** config file, build the app again and release it to the new destination.

### 2.8 pre-commit hooks

Don't forget to install the pre-commit hooks:

```powershell
pre-commit install
```

### 2.9 docs

Documentation is done with [pdoc3](https://pdoc3.github.io/pdoc/).

To update the documentation run:

```powershell
python -m pdoc --html --output-dir docs pytia_bill_of_material
```

For preview run:

```powershell
python -m pdoc --http : pytia_bill_of_material
```

You can find the documentation in the [docs folder](/docs).

### 2.10 new revision checklist

On a new revision, do the following:

1. Update **dependency versions** in
   - [pyproject.toml](pyproject.toml)
   - [dependencies.json](pytia_bill_of_material/resources/dependencies.json)
   - [README.md](README.md)
2. Update **dependencies**: `poetry update`
3. Update the **version** in
   - [pyproject.toml](pyproject.toml)
   - [__ init __.py](pytia_bill_of_material/__init__.py)
   - [README.md](README.md)
4. Run all **tests**: `poetry run pytest`
5. Check **pylint** output: `poetry run pylint pytia_bill_of_material/`
6. Update the **documentation**: `poetry run pdoc --force --html --output-dir docs pytia_bill_of_material`
7. Update the **lockfile**: `poetry lock`
8. Update the **requirements.txt**: `poetry export --dev -f requirements.txt -o requirements.txt`

## 3 usage

Use the launcher (a.k.a the catvbs-file) to launch the app. On the first run all required dependencies will be installed:

![Installer](assets/images/installer.png)

After the installation the app starts automatically:

![App](assets/images/app.png)

The app retrieves all information from the documents properties, except the material value, which is fetched from the applied material.

The usage itself is pretty straight forward, as long as all config files are setup properly.

Object | Description
--- | ---
Project | The user can overwrite the project number for all items of the bill of material. If set to `Keep` no project number will be overwritten.
Bill of Material File | The full path to the bill of material xlsx file. The folder must exist, otherwise the `Export` button will be disabled.
Docket Folder | The folder into which all generated docket files will be stored. The folder must exist, otherwise the `Export Docket` checkbox will be disabled.
Drawing Folder | The folder into which all drawing files (pdf and dxf) will be stored. The folder must exist, otherwise the `Export Drawings` checkbox will be disabled.
STP Folder | The folder into which all generated step files will be stored. The folder must exist, otherwise the `Export STP` checkbox will be disabled.
STL Folder | The folder into which all generated stl files will be stored. The folder must exist, otherwise the `Export STL` checkbox will be disabled.

### 3.1 report

If the export fails because any criteria from the `filters.json` aren't satisfied, the report window will be opened. This allows the user to see which item from the bill of material fails:

![Report](assets/images/report.png)

## 4 workspace

The workspace is an **optional** config file, that can be used to alter the behavior of the app. The workspace file is a yaml-file, which must be saved somewhere in the project directory, where the catia document, from which to manage the properties, is also stored:

```bash
your-fancy-project
├─── main.CATProduct
├─── subfolder-A
│    ├─── product-A.CATProduct
│    ├─── part-A-01.CATPart
│    └─── part-A-02.CATPart
├─── subfolder-B
│    ├─── product-B.CATProduct
│    ├─── part-B-01.CATPart
│    └─── part-B-02.CATPart
└─── workspace.yml
```

As long as the workspace file is located somewhere in the project, and as long as this file is in the **same** folder, or any folder **above** the CATProduct file, it will be used.

For a detailed description of the workspace config file, see [WORKSPACE_FILE](docs/WORKSPACE_FILE.md).

The filename of the workspace file can be changed in the **settings.json** file, see [SAMPLE_FILES](docs/SAMPLE_FILES.md).

## 5 license

[MIT License](LICENSE)

## 6 changelog

**v0.3.1**: Fix drawing path bug.  
**v0.3.0**: Add drawing export feature.  
**v0.2.0**: Add report document handler and log console.  
**v0.1.2**: Fix deleting template files too early.  
**v0.1.1**: Add failed property description.  
**v0.1.0**: Initial commit.  

## 7 to dos

Using VS Code [Comment Anchors](https://marketplace.visualstudio.com/items?itemName=ExodiusStudios.comment-anchors) to keep track of to-dos.
