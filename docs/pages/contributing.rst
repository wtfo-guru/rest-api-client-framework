
How to contribute
=================

Dependencies
------------

We use `poetry <https://github.com/python-poetry/poetry>`_ to manage the dependencies.

To install/update them you would need to run command:

.. code-block:: bash

   make update

One magic command
-----------------

Run ``make test`` to run everything we have!

Tests
-----

We use ``flake8`` and ``pytest`` for quality control.
We also use `wemake_python_styleguide <https://github.com/wemake-services/wemake-python-styleguide>`_ to enforce the code quality.

To run all tests:

.. code-block:: bash

   make unit

To run linting:

.. code-block:: bash

   make lint

Type checks
-----------

We use ``mypy`` to run type checks on our code.
To use it:

.. code-block:: bash

   make mypy

This step is mandatory during the CI.

Submitting your code
--------------------

What the point of this method?


#. We use protected ``main`` branch,
   so the only way to push your code is via pull request
#. We use issue branches: to implement a new feature or to fix a bug
   create a new branch named ``issue-$TASKNUMBER``
#. Then create a pull request to ``main`` branch
#. We use ``git tag``\ s to make releases, so we can track what has changed
   since the latest release

So, this way we achieve an easy and scalable development process
which frees us from merging hell and long-living branches.

In this method, the latest version of the app is always in the ``main`` branch.

Before submitting
^^^^^^^^^^^^^^^^^

Before submitting your code please do the following steps:


#. Run ``make test`` to make sure everything was working before
#. Add any changes you want
#. Add tests for the new changes
#. Edit documentation if you have changed something significant
#. Run ``make test`` again to make sure it is still working

Other help
----------

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
