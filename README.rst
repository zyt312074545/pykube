.. image:: https://raw.githubusercontent.com/zyt312074545/pykubeyaml/master/Logo.png
    :align: center

pykubeyaml
==============================================

.. image:: https://travis-ci.org/zyt312074545/pykubeyaml.svg?branch=master
    :target: https://travis-ci.org/zyt312074545/pykubeyaml

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT

----------------------------------------------

**pykubeyaml** is a tool that aims to Automate Kubernetes workflow, It automatically
creates yaml file.

.. image:: https://raw.githubusercontent.com/zyt312074545/pykubeyaml/master/pykubeyaml.gif

Installation
------------

.. code-block:: bash

    $ pip install pykubeyaml

Usage
-------

.. code-block:: bash

    $ pykubeyaml
    Usage: pykubeyaml [OPTIONS] COMMAND [ARGS]...

      Use for kubernetes, designed to automate Kubernetes workflow.

    Options:
      --help  Show this message and exit.

    Commands:
      generate  Use for generate kubernetes yaml file.

Generate the yaml file:

.. code-block:: bash

    $ pykubeyaml generate --help
    Usage: pykubeyaml generate [OPTIONS]

      Use for generate kubernetes yaml file.

    Options:
      --kind [deployment|service|ingress]
                                      The kind of yaml.
      --help                          Show this message and exit.

