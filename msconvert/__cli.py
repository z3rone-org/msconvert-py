import os
from msconvert import MSConvertRunner
import docker
from time import sleep
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Rescoring crosslinked-peptide identifications.')
    parser.add_argument('-i', action='store', dest='workdir', help='input path',
                        default=Path.cwd(), type=str, required=False)
    parser.add_argument('--input-format', action='store', dest='in_format', help='input format',
                        default="raw", type=str, required=False)
    parser.add_argument('--output-format', action='store', dest='out_format', help='output format',
                        default="mgf", type=str, required=False)
    parser.add_argument('--concurrency', action='store', dest='concurrency', help='maximum concurrency',
                        default=os.cpu_count(), type=int, required=False)
    args = parser.parse_args()

    client = docker.from_env()
    workdir = args.workdir
    in_format = args.in_format
    out_format = args.out_format
    concurrency = args.concurrency

    runner = MSConvertRunner(
        workdir,
        in_format=in_format,
        out_format=out_format,
        client=client,
        concurrency=concurrency
    )

    while True:
        runner.update()
        pend = len(runner.get_pending_jobs())
        runn = len(runner.get_running_jobs())
        fail = len(runner.get_failed_jobs())
        rsvd = runner.get_reserved_mem()
        if (pend == 0) and (runn == 0) and (fail == 0):
            break
        print(f'pending: {pend}, running: {runn}, failed: {fail}, reserved: {rsvd}G')
        sleep(5)
    runner.cleanup()


if __name__ == "__main__":
    main()