"""
    Submodule for common classes and functions.
"""

import re


class ResourceCommons:
    @staticmethod
    def get_property_names_from_config(header: list) -> tuple:
        """
        Returns a tuple containing the property names of the bom.json header items.
        Returns the header name if an item is not a property.
        """
        prop_names = ()
        for item in header:
            if ":" in item:
                prop_names += (item.split(":")[-1],)
            elif "=" in item:
                prop_names += (item.split("=")[0],)
            else:
                prop_names += (item,)
        return prop_names

    @staticmethod
    def get_header_names_from_config(header: list) -> tuple:
        """
        Returns a tuple containing the header names of the bom.json header items.
        """
        return tuple([s for s in re.split("[:|=]+", i)][0] for i in header)
