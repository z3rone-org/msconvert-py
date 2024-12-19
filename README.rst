msconvert-py
============

A Python wrapper for the `pwiz/msconvert docker image <https://hub.docker.com/r/proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses>`_.

Why?
----

In my personal experience, running the docker container directly may cause some problems:

- On large machines, the containers consume a lot of memory because the garbage collection rarely kicks in.
- Memory seems to leak when rescoring multiple files in one msconvert run.
- Limiting the memory usage is difficult because conversion may require somewhere between ~3G and ~30G.
- The conversion is single-threaded.

How to Run
----------

Install the package via:

.. code-block:: bash

    pip install msconvert

Run it via:

.. code-block:: bash

    python -m msconvert

By default, the module will convert every ``*.raw`` file in the current directory to ``.mgf``. However, there are other options available:

- ``-i``: Input path (default is current directory)
- ``--input-format``: Input format (default ``raw``)
- ``--output-format``: Output format (default ``mgf``)
- ``--concurrency``: Concurrency (default is the number of cores)

How it Works
------------

- **msconvert-py** runs each conversion in a dedicated docker container.
- Each container is initially limited to 3G memory.
- When a container fails due to an out-of-memory kill, it will be re-run with an additional 8G memory.
- The containers run concurrently, by default up to the number of cores.
- Containers are only started when memory is available within the defined memory limit.
