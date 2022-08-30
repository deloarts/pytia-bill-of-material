# default files

Explains the config of all default files.

All default files can be copied, renamed and edited to fit your needs.

## 1 bom.default.json

This file contains the configuration for the final bill of material excel file.

- **Location**: [/pytia_bill_of_material/resources/bom.default.json](../pytia_bill_of_material/resources/bom.default.json)
- **Rename to**: `bom.json`

### 1.1 file content

```json
{
    "header_row": 0,
    "data_row": 1,
    "header_items": [
        "pytia.project",
        "pytia.machine",
        "$number",
        "$type",
        "$quantity",
        "$partnumber",
        "$definition",
        "$revision",
        "pytia.material",
        "pytia.base_size",
        "pytia.base_size_preset",
        "pytia.mass",
        "$source",
        "pytia.manufacturer",
        "pytia.supplier",
        "pytia.spare_part_level",
        "pytia.tolerance",
        "pytia.creator",
        "pytia.modifier",
        "$description",
        "pytia.note_general",
        "pytia.note_material",
        "pytia.note_base_size",
        "pytia.note_supplier",
        "pytia.note_production",
        "pytia.process_1",
        "pytia.note_process_1",
        "pytia.process_2",
        "pytia.note_process_2",
        "pytia.process_3",
        "pytia.note_process_3",
        "pytia.process_4",
        "pytia.note_process_4",
        "pytia.process_5",
        "pytia.note_process_5",
        "pytia.process_6",
        "pytia.note_process_6"
    ],
    "required_header_items": {
        "project": "pytia.project",
        "machine": "pytia.machine",
        "partnumber": "$partnumber",
        "revision": "$revision",
        "quantity": "$quantity"
    },
    "sort": {
        "made": "$partnumber",
        "bought": "pytia.manufacturer"
    },
    "font": "Monospac821 BT",
    "size": 8,
    "header_color": "FFFFFF",
    "header_bg_color": "007ACC",
    "data_color_1": "000000",
    "data_bg_color_1": "F0F0F0",
    "data_color_2": "000000",
    "data_bg_color_2": "FFFFFF"
}
```

### 1.2 description

name | type | description
--- | --- | ---
header_row | `int` | The row number which shows the header. This value is zero-indexed, add `1` to match the row in Excel.
data_row | `int` | The row number from which the data will be written. This value is zero-indexed, add `1` to match the row in Excel.
header_items | `list` | A list of the header items that will be shown in the final export in the order of this list. These header items represent the properties of the parts and products. User-properties can be added by their name, CATIA properties and special properties must be added with a dollar sign `$` prefix (see keywords.json).
required_header_items | `list` | A list of items, that must be included in the `header_items` list. Make sure, that the keywords between those two lists match.
sort.made | `str` | The header_item by which to sort the made-ist.
sort.bought | `str` | The header_item by which to sort the bought-list.
font | `str` | The font of the final bill of material.
size | `int` | The font size of the final bill of material.
header_color | `str` | The header font color of the final bill of material.
header_bg_color | `str` | The header background color of the final bill of material.
data_color_1 | `str` | The font color for each even row of the final bill of material.
data_bg_color_1 | `str` | The background color for each even row of the final bill of material.
data_color_2 | `str` | The font color for each odd row of the final bill of material.
data_bg_color_2 | `str` | The background color for each odd row of the final bill of material.

## 2 filters.default.json

This file contains the set of rules by which the items of the bill of material are going to be tested against.

- **Location**: [/pytia_bill_of_material/resources/filters.default.json](../pytia_bill_of_material/resources/filters.default.json)
- **Rename to**: `filters.json`

### 2.1 file content

```json
[
    {
        "property_name": "$number",
        "criteria": "^\\d+$",
        "condition": {
            "$type": "$part"
        },
        "description": "The number must be set. Have you forgotten to run the 'Generate Numbering' command?"
    },
    {
        "property_name": "$revision",
        "criteria": "^\\d+$",
        "condition": true,
        "description": "The revision must be a number."
    },
    {
        "property_name": "pytia.material",
        "criteria": ".*",
        "condition": {
            "$type": "$part",
            "$source": "$made"
        },
        "description": "The material must be set for 'made' parts."
    },
    ...
]
```

### 2.2 description

name | type | description
--- | --- | ---
property_name | `str` | The name of the property that is being tested. Note: This is not the name of a part/product property, it is the name of the item from the `header_items` list from the `bom.json` config file.
criteria | `str` | The criteria that must be satisfied. Use regular expressions for matching.
condition | `dict` or `bool` | The condition that must be satisfied in order to match the criteria with the value of the property. If the condition is not satisfied, the property won't be tested against the criteria.<br><br>If `bool`: When `true`, the criterial must always be satisfied for the property.<br><br>If `dict`: The dict represents properties as keys and the condition for this property as values. Only if all dict-items are satisfied the criteria will be tested against the value of the property. Example: See the file content above: The property `pytia.material` must not be empty (criteria=`.*`), but only if the document type is a part and the source is made. (`$type`, `$source`, `$made` and `$part` are all special keywords, see the keywords.json)
description | `str` | A human readable description of the criteria. Will be visible in the report.

## 3 information.default.json

This file contains a list of information, which will be shown to the user when the app has been used `counter` times.

- **Location**: [/pytia_bill_of_material/resources/information.default.json](../pytia_bill_of_material/resources/information.default.json)
- **Rename to**: `information.json`

### 3.1 file content

```json
[
    {
        "counter": 5,
        "msg": "If you need help using this app, or if you just want to know more about the available features: Press F1."
    },
    ...
]
```

### 3.2 description

name | type | description
--- | --- | ---
counter | `int` | The amount of app-usages when the information is shown.
id | `str` | The message to show.

## 4 properties.default.json

This file contains all part properties, which are required for this app.

- **Location**: [/pytia_bill_of_material/resources/properties.default.json](../pytia_bill_of_material/resources/properties.default.json)
- **Rename to**: `properties.json`

### 4.1 file content

```json
{
    "project": "pytia.project",
    "machine": "pytia.machine",
    "creator": "pytia.creator",
    "modifier": "pytia.modifier"
}
```

### 4.2 description

name | type | description
--- | --- | ---
`generic` | `str` | The name of the property, which stores the value of `generic`.
