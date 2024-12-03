# usage

> ✏️ This covers the usage of the app, which depends on the configuration of the `settings.json` config file. If you use different names for properties or disable some of the functionality, the apps layout may be different from the one in this guide.

- [usage](#usage)
  - [1 launcher](#1-launcher)
  - [2 app](#2-app)
    - [2.1 export structure](#21-export-structure)
      - [2.1.1 default](#211-default)
      - [2.1.2 bundle data](#212-bundle-data)
      - [2.1.3 bundle data with zip bundle](#213-bundle-data-with-zip-bundle)
      - [2.1.4 bundle data with bundle by property](#214-bundle-data-with-bundle-by-property)
    - [2.1 report](#21-report)

## 1 launcher

If your setup is done (see [installation](./INSTALLATION.md)), open the app from within CATIA. If this is the first time, you'll see the launcher will install all necessary dependencies:

![Installer](/assets/images/installer.png)

After the installation you can run the app.

## 2 app

The usage itself is pretty straight forward, as long as all config files are setup properly.

![app](/assets/images/app.png)

Object | Description
--- | ---
Project | The user can overwrite the project number for all export-items of the bill of material. This **does not** overwrite the project number in the properties of each item, the project number will only be used for the export data. If set to `Keep` the original project number of each item will be used.
Bill of Material File | The full path to the bill of material xlsx file. The folder must exist, otherwise the `Export` button will be disabled.
Docket Folder | The folder into which all generated docket files will be stored. The template-CATDrawing file and the export folder must exist, otherwise the `Export Docket` checkbox will be disabled.
Documentation Folder | The folder into which all generated documentation docket files will be stored. The template-CATDrawing file and the export folder must exist, otherwise the `Export Documentation` checkbox will be disabled.
Drawing Folder | The folder into which all drawing files (pdf and dxf) will be stored. The folder must exist, otherwise the `Export Drawings` checkbox will be disabled. Note: Drawings can only be exported, if the CATDrawing file is linked to the CATPart or CATProduct. This can be done with the `Title Block Editor` app or the `Property Manager`app.
STP Folder | The folder into which all generated step files will be stored. The folder must exist, otherwise the `Export STP` checkbox will be disabled.
STL Folder | The folder into which all generated stl files will be stored. The folder must exist, otherwise the `Export STL` checkbox will be disabled.
JPG Folder | The folder into which all generated jpg files will be stored. The folder must exist, otherwise the `Export JPG` checkbox will be disabled.
Bundle Data | Instead of exporting all file types into different folders separately, with this option enabled all exported data of one item are stored in a folder with the items' partnumber. In other words: Everything in one place. See description below.
ZIP Bundle | If enabled, the folder containing the bundled data will be zipped. See description below.
Bundle by property | All bundled data can be sorted by the selected property. The properties' value will represent the folder name. See description below.
Ignore Unknown | Ignores all product tree nodes with the source `unknown`.
Ignore Prefixed | Ignores all product tree nodes where their partnumber start with the given prefixes. Prefixes can be separated by a semicolon.

### 2.1 export structure

#### 2.1.1 default

Default means `Bundle Data` is turned off, everything will be exported into separate folders by their type (Docket, Drawing, STP, ...).
The following tree represents the export by the given input of the picture above.

```bash
export folder (E:\pytia)
├─── dockets
│    ├─── Part-A.pdf (the generated pdf docket)
│    ├─── Part-B.pdf
│    └─── ...
├─── drawings
│    ├─── Part-A.pdf (the CATDrawing file as pdf)
│    ├─── Part-A.dxf (the CATDrawing file as dxf)
│    ├─── Part-B.pdf
│    ├─── Part-B.dxf
│    └─── ...
└─── 3d-data
│    ├─── Part-A.stp (the CATPart file as step)
│    ├─── Part-A.stl (the CATPart file as stl)
│    ├─── Part-B.stp
│    ├─── Part-B.stl
│    └─── ...
└─── ...
```

#### 2.1.2 bundle data

When `Bundle Data` is enabled, all items will be exported into folders representing their partnumber.

```bash
export folder (E:\pytia)
├─── Part-A
│    ├─── Part-A.Docket.pdf (the generated pdf docket)
│    ├─── Part-A.pdf (the CATDrawing file as pdf)
│    ├─── Part-A.dxf (the CATDrawing file as dxf)
│    ├─── Part-A.stp (the CATPart file as step)
│    ├─── Part-A.stl (the CATPart file as stl)
│    └─── ...
├─── Part-B
│    ├─── Part-B.Docket.pdf
│    ├─── Part-B.pdf
│    ├─── Part-B.dxf
│    ├─── Part-B.stp
│    ├─── Part-B.stl
│    └─── ...
└─── ...
```

#### 2.1.3 bundle data with zip bundle

When `Bundle Data` and `ZIP Bundle` is enabled, all items will be exported into zip files representing their partnumber.

```bash
export folder (E:\pytia)
├─── Part-A.zip
│    ├─── Part-A.Docket.pdf (the generated pdf docket)
│    ├─── Part-A.pdf (the CATDrawing file as pdf)
│    ├─── Part-A.dxf (the CATDrawing file as dxf)
│    ├─── Part-A.stp (the CATPart file as step)
│    ├─── Part-A.stl (the CATPart file as stl)
│    └─── ...
├─── Part-B.zip
│    ├─── Part-B.Docket.pdf
│    ├─── Part-B.pdf
│    ├─── Part-B.dxf
│    ├─── Part-B.stp
│    ├─── Part-B.stl
│    └─── ...
└─── ...
```

#### 2.1.4 bundle data with bundle by property

When `Bundle Data` and `Bundle By Property` is enabled, all items will be exported into folders representing their partnumber, and those folders will be in a main-folder, representing the value of the selected property.

Example below: The selected property is `Process 1`, where the parts have the following first process:

- Part-A: Milling
- Part-B: Turning
- Part-C: Milling

```bash
export folder (E:\pytia)
├─── Milling
│    ├─── Part-A.zip
│    │    ├─── Part-A.Docket.pdf (the generated pdf docket)
│    │    ├─── Part-A.pdf (the CATDrawing file as pdf)
│    │    ├─── Part-A.dxf (the CATDrawing file as dxf)
│    │    ├─── Part-A.stp (the CATPart file as step)
│    │    ├─── Part-A.stl (the CATPart file as stl)
│    │    └─── ...
│    └─── Part-C.zip
│         ├─── Part-C.Docket.pdf
│         ├─── Part-C.pdf
│         ├─── Part-C.dxf
│         ├─── Part-C.stp
│         ├─── Part-C.stl
│         └─── ...
├─── Turning
│    └─── Part-B.zip
│         ├─── Part-B.Docket.pdf
│         ├─── Part-B.pdf
│         ├─── Part-B.dxf
│         ├─── Part-B.stp
│         ├─── Part-B.stl
│         └─── ...
└─── ...
```

### 2.1 report

If the export fails because any criteria from the `filters.json` aren't satisfied, the report window will be opened. This allows the user to see which item from the bill of material fails:

![Report](/assets/images/report.png)
