# msconvert-py

A python wrapper for the [pwiz/msconvert docker image](https://hub.docker.com/r/proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses).

# Why?

In my personal experience running the docker container directly may cause some problems:

- On large machines the containers eat up a lot of memory because the garbage collection rarely kicks in.
- Memory seems to leak when rescoring multiple files in one msconvert run.
- Limiting the memory usage is difficult because conversion may require somewhere between ~3G and ~30G.
- The conversion is single threaded.

# How to run

Install the package via `pip install msconvert` and run it via `python -m msconvert`.

By default, the module will convert every `*.raw` file in the current directory to `.mgf`.
However, there are other options available:

- `-i` Input path (default is current directory)
- `--input-format` Input format (default `raw`)
- `--output-format` Output format (default `mgf`)
- `--concurrency` Concurrency (default is number of cores)

# How it works

- Msconvert-py runs each conversion in a dedicated docker container.
- Each container is initially limited to 3G memory.
- When a container fails due to an out-of-memory kill it will be re-run with +8G memory.
- The containers run concurrent, per default up to the number of cores.
- Containers are only started as soon as there is memory available as defined to the memory limit.