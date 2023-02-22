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
    "files": {
        "separate": true,
        "summary": "Summary",
        "made": "Made",
        "bought": "Bought"
    },
    "header_items": {
        "summary": [
            "Project:pytia.project",
            "Machine:pytia.machine",
            "Number:$number",
            "Type:$type",
            "Quantity:$quantity",
            "Unit=PCS",
            "Partnumber:$partnumber",
            "Definition:$definition",
            "Rev:$revision",
            "Material:pytia.material",
            "Base Size:pytia.base_size",
            "Base Size Preset:pytia.base_size_preset",
            "Mass:pytia.mass",
            "Source:$source",
            "Manufacturer:pytia.manufacturer",
            "Supplier:pytia.supplier",
            "SPL:pytia.spare_part_level",
            "Tolerance:pytia.tolerance",
            "Creator:pytia.creator",
            "Modifier:pytia.modifier",
            "Description:$description",
            "Note:pytia.note_general",
            "Note Material:pytia.note_material",
            "Note Base Size:pytia.note_base_size",
            "Note Supplier:pytia.note_supplier",
            "Note Production:pytia.note_production",
            "Process 1:pytia.process_1",
            "Note Process 1:pytia.note_process_1",
            "Process 2:pytia.process_2",
            "Note Process 2:pytia.note_process_2",
            "Process 3:pytia.process_3",
            "Note Process 3:pytia.note_process_3",
            "Process 4:pytia.process_4",
            "Note Process 4:pytia.note_process_4",
            "Process 5:pytia.process_5",
            "Note Process 5:pytia.note_process_5",
            "Process 6:pytia.process_6",
            "Note Process 6:pytia.note_process_6"
        ],
        "made": [
            "Project:pytia.project",
            "Machine:pytia.machine",
            "Number:$number",
            "Type:$type",
            "Quantity:$quantity",
            "Unit=PCS",
            "Partnumber:$partnumber",
            "Definition:$definition",
            "Rev:$revision",
            "Material:pytia.material",
            "Base Size:pytia.base_size",
            "Base Size Preset:pytia.base_size_preset",
            "Mass:pytia.mass",
            "Manufacturer:pytia.manufacturer",
            "Supplier:pytia.supplier",
            "SPL:pytia.spare_part_level",
            "Tolerance:pytia.tolerance",
            "Creator:pytia.creator",
            "Modifier:pytia.modifier",
            "Description:$description",
            "Note:pytia.note_general",
            "Note Material:pytia.note_material",
            "Note Base Size:pytia.note_base_size",
            "Note Supplier:pytia.note_supplier",
            "Note Production:pytia.note_production",
            "Process 1:pytia.process_1",
            "Note Process 1:pytia.note_process_1",
            "Process 2:pytia.process_2",
            "Note Process 2:pytia.note_process_2",
            "Process 3:pytia.process_3",
            "Note Process 3:pytia.note_process_3",
            "Process 4:pytia.process_4",
            "Note Process 4:pytia.note_process_4",
            "Process 5:pytia.process_5",
            "Note Process 5:pytia.note_process_5",
            "Process 6:pytia.process_6",
            "Note Process 6:pytia.note_process_6"
        ],
        "bought": [
            "Project:pytia.project",
            "Machine:pytia.machine",
            "Number:$number",
            "Type:$type",
            "Quantity:$quantity",
            "Unit=PCS",
            "Partnumber:$partnumber",
            "Definition:$definition",
            "Rev:$revision",
            "Mass:pytia.mass",
            "Manufacturer:pytia.manufacturer",
            "Supplier:pytia.supplier",
            "SPL:pytia.spare_part_level",
            "Creator:pytia.creator",
            "Modifier:pytia.modifier",
            "Description:$description",
            "Supplier:pytia.note_supplier"
        ]
    },
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
files.separate | `bool`| If `True` this will create separate excel files for the three categories `summary`, `made` and `bought`.
files.summary | `str`| The text which will be added to the filename of the exported summary-excel file, if `files.separate` is set to `True`. Format: `filename (files.summary).xlsx`.
files.made | `str`| The text which will be added to the filename of the exported made-parts-excel file, if `files.separate` is set to `True`. Format: `filename (files.made).xlsx`.
files.bought | `str`| The text which will be added to the filename of the exported bought-parts-excel file, if `files.separate` is set to `True`. Format: `filename (files.bought).xlsx`.
header_items.summary | `list` | A list of the header items for the summary that will be shown in the final export as worksheet in the order of this list. These header items must be defined with the following syntax: `HEADER NAME:PROPERTY NAME` or `HEADER NAME=FIXED TEXT`<br><ul><li>User-properties can be added by their name. E.g.: If you want the project number to have the header name "Project", you have to write the value as `Project:pytia.project` (assuming that the project number is stores as 'pytia.project' in the document's properties).</li><li>CATIA properties and special properties must be added with a dollar sign `$` prefix (see keywords.json). E.g.: To add the partnumber you have to write it like this: `Part Number:$partnumber`. This creates the column **Part Number**.</li><li>Further it is possible to apply *fixed text*. This is done with header name followed by the equal sign `=` and then followed by the value of that fixed text. E.g: If you want a column **Unit** with the text **Pcs** in every item of the bom, you have to add `"Unit=Pcs"` to the header_items list.</li><li>An item that has neither a double point `:`, not an equal sign `=` in it will represent an empty row, with the value as header name.</li></ul>
header_items.made | `list` or null | A list of the header items for all made items in the final export. Important note: All items that are in this list must be present in the *header_items.summary* list, otherwise the values for this columns will be empty. If set to `null` no made worksheet will be exported.
header_items.bought | `list` or null | A list of the header items for all bought items in the final export. Important note: All items that are in this list must be present in the *header_items.summary* list, otherwise the values for this columns will be empty. If set to `null` no bought worksheet will be exported.
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
