"""
    Test the resources.py file.
"""

import os

import validators


def test_resources_class():
    from pytia_bill_of_material.resources import Resources

    resource = Resources()


def test_settings():
    from pytia_bill_of_material.resources import resource

    assert isinstance(resource.settings.title, str)
    assert len(resource.settings.title) > 0
    assert isinstance(resource.settings.debug, bool)

    assert isinstance(resource.settings.export.apply_username_in_bom, bool)
    assert isinstance(resource.settings.export.apply_username_in_docket, bool)

    assert isinstance(resource.settings.restrictions.allow_all_users, bool)
    assert isinstance(resource.settings.restrictions.allow_all_editors, bool)
    assert isinstance(resource.settings.restrictions.allow_unsaved, bool)
    assert isinstance(resource.settings.restrictions.allow_outside_workspace, bool)
    assert isinstance(resource.settings.restrictions.strict_project, bool)
    assert isinstance(resource.settings.restrictions.enable_information, bool)

    assert isinstance(resource.settings.paths.catia, str)
    assert isinstance(resource.settings.paths.local_dependencies, str)
    assert isinstance(resource.settings.paths.release, str)

    assert isinstance(resource.settings.files.bom_export, str)
    assert isinstance(resource.settings.files.app, str)
    assert isinstance(resource.settings.files.launcher, str)
    assert isinstance(resource.settings.files.workspace, str)

    if resource.settings.urls.help:
        assert validators.url(resource.settings.urls.help)  # type: ignore
    assert validators.email(resource.settings.mails.admin)  # type: ignore


def test_properties():
    from pytia_bill_of_material.resources import resource

    assert "project" in resource.props.keys
    assert "machine" in resource.props.keys
    assert "creator" in resource.props.keys
    assert "modifier" in resource.props.keys


def test_users():
    from pytia_bill_of_material.resources import resource

    logon_list = []

    for user in resource.users:
        assert isinstance(user.logon, str)
        assert isinstance(user.id, str)
        assert isinstance(user.name, str)
        assert isinstance(user.mail, str)
        assert user.logon not in logon_list

        logon_list.append(user.logon)


def test_template_files():
    from pytia_bill_of_material.const import TEMPLATE_DOCKET

    # assert os.path.exists(Path("./pytia_bill_of_material/templates", TEMPLATE_DOCKET))


def test_local_dependencies_folder():
    from pytia_bill_of_material.resources import resource

    assert os.path.isdir(resource.settings.paths.local_dependencies)


def test_release_folder():
    from pytia_bill_of_material.resources import resource

    assert os.path.isdir(resource.settings.paths.release)


def test_debug_mode():
    from pytia_bill_of_material.resources import resource

    assert resource.settings.debug == False
