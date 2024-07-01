===========
Restful API
===========

Enables a REST API for the Odoo server. The API has routes to
authenticate and retrieve a token. Afterwards, a set of routes to
interact with the server are provided.

Requirements
=============

OAuthLib
-------------

A generic, spec-compliant, thorough implementation of the OAuth request-signinglogic
for Python. To install OAuthLib please follow the `instructions <https://pypi.org/project/oauthlib/>`_
or install the library via pip.

``pip install oauthlib``

Installation
============

To install this module, you need to:

Download the module and add it to your Odoo addons folder. Afterward, log on to
your Odoo server and go to the Apps menu. Trigger the debug mode and update the
list by clicking on the "Update Apps List" link. Now install the module by
clicking on the install button.

Another way to install this module is via the package management for Python
(`PyPI <https://pypi.org/project/pip/>`_).

To install our modules using the package manager make sure
`odoo-autodiscover <https://pypi.org/project/odoo-autodiscover/>`_ is installed
correctly. Then open a console and install the module by entering the following
command:

``pip install --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

The module name consists of the Odoo version and the module name, where
underscores are replaced by a dash.

**Module:** 

``odoo<version>-addon-<module_name>``

**Example:**

``sudo -H pip3 install --extra-index-url https://nexus.mukit.at/repository/odoo/simple odoo11-addon-muk-utils``

Once the installation has been successfully completed, the app is already in the
correct folder. Log on to your Odoo server and go to the Apps menu. Trigger the 
debug mode and update the list by clicking on the "Update Apps List" link. Now
install the module by clicking on the install button.

The biggest advantage of this variant is that you can now also update the app
using the "pip" command. To do this, enter the following command in your console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo. The steps are the same as for the installation only the button has changed
from "Install" to "Upgrade".

You can also view available Apps directly in our `repository <https://nexus.mukit.at/#browse/browse:odoo>`_
and find a more detailed installation guide on our `website <https://mukit.at/page/open-source>`_.

For modules licensed under OPL-1, you will receive access data when you purchase
the module. If the modules were not purchased directly from
`MuK IT <https://www.mukit.at/>`_ please contact our support (support@mukit.at)
with a confirmation of purchase to receive the corresponding access data.

Upgrade
============

To upgrade this module, you need to:

Download the module and add it to your Odoo addons folder. Restart the server
and log on to your Odoo server. Select the Apps menu and upgrade the module by
clicking on the upgrade button.

If you installed the module using the "pip" command, you can also update the
module in the same way. Just type the following command into the console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo, just like you would normally.

Configuration
=============

In case the module should be active in every database just change the
auto install flag to ``True``. To activate the routes even if no database
is selected the module should be loaded right at the server start. This
can be done by editing the configuration file or passing a load parameter to
the start script.

Parameter: ``--load=web,muk_rest``

To configure this module, you need to:

#. Go to *Settings -> Restful API -> Dashboard*. Here you can see an overview of all your APIs.
#. Click on *Create* or go to either *Restful API -> OAuth1* or *Restful API -> OAuth2* to create a new API.

Usage
=============

This module provides a set of routes to interact with the system via HTTP requests.
Take a look at the `clients <https://github.com/muk-it/muk_docs/blob/12.0/muk_rest/clients/clients.md>`_
and `examples <https://github.com/muk-it/muk_docs/blob/12.0/muk_rest/examples/examples.md>`_ or open
the `documentation <https://app.swaggerhub.com/apis/keshrath/muk_rest/docs/3.0.0/>`_ to get a detailed
description of every available route.

Credits
=======

Contributors
------------

* Mathias Markl <mathias.markl@mukit.at>

Images
------------

Some pictures are based on or inspired by:

* `Font Awesome <https://fontawesome.com>`_
* `Prosymbols <https://www.flaticon.com/authors/prosymbols>`_
* `Smashicons <https://www.flaticon.com/authors/smashicons>`_

Author & Maintainer
-------------------

This module is maintained by the `MuK IT GmbH <https://www.mukit.at/>`_.

MuK IT is an Austrian company specialized in customizing and extending Odoo.
We develop custom solutions for your individual needs to help you focus on
your strength and expertise to grow your business.

If you want to get in touch please contact us via mail
(sale@mukit.at) or visit our website (https://mukit.at).
