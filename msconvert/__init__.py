import docker
import os
import psutil
import sys

class MSConvertJob:
    def __init__(self, file, workdir, out_format, mem_limit, client):
        # Check if image is pulled
        image_tags = []
        pwiz_tag = 'chambm/pwiz-skyline-i-agree-to-the-vendor-licenses:latest'
        for image in client.images.list():
            image_tags += image.tags
        if pwiz_tag not in image_tags:
            print(
                f'Image {pwiz_tag} not pulled. You need to pull this yourself to avoid license conflicts.',
                file=sys.stderr
            )
            sys.exit(1)
        self.file = file
        self.workdir = workdir
        self.out_format = out_format
        self.mem_limit = mem_limit
        self.container = None
        self.client = client
        self.attempt = 0

    def run(self):
        self.attempt += 1
        with open(f'{self.workdir}/{self.file}.lst', 'w') as lstf:
            lstf.write(self.file)
        if self.container is not None:
            self.container.remove()
        self.mem_limit = self.next_mem_limit()
        self.container = self.client.containers.run(
            "chambm/pwiz-skyline-i-agree-to-the-vendor-licenses",
            f"wine msconvert --{self.out_format} -v -f {self.file}.lst",
            mem_limit=f'{self.mem_limit}g',
            mem_swappiness=0,
            mounts=[docker.types.Mount('/data', self.workdir, type='bind')],
            detach=True,
        )

    def next_mem_limit(self):
        if self.container is not None and self.container.attrs['State']['OOMKilled']:
            return self.mem_limit + 8
        else:
            return self.mem_limit


class MSConvertRunner:
    def __init__(self, workdir, in_format, out_format, client, concurrency=10):
        self.workdir = workdir
        self.in_format = in_format
        self.out_format = out_format
        self.concurrency = concurrency
        self.client = client
        # Create pending jobs
        self.jobs = []
        in_files = self.get_input_files()
        if len(in_files) == 0:
            ext = self.in_format.lower()
            print(f'No .{ext}-files found in {self.workdir}')
            sys.exit(2)
        for f in self.get_input_files():
            self.jobs.append(
                MSConvertJob(
                    f,
                    workdir,
                    self.out_format,
                    3,
                    self.client
                )
            )

    def get_input_files(self):
        ext = self.in_format.lower()
        return [
            f
            for f in os.listdir(self.workdir)
            if f.lower().endswith(f'.{ext}')
        ]

    def get_free_mem(self):
        return psutil.virtual_memory().available / 1024 / 1024 // 1024

    def get_running_jobs(self):
        self.update_containers()
        return [
            j
            for j in self.jobs
            if (
                    j.container is not None and
                    j.container.attrs['State']['Running']
            )
        ]

    def get_pending_jobs(self):
        self.update_containers()
        return [
            j
            for j in self.jobs
            if j.container is None
        ]

    def get_failed_jobs(self):
        self.update_containers()
        return [
            j
            for j in self.jobs
            if (
                    j.container is not None and
                    not j.container.attrs['State']['Running'] and (
                            j.container.attrs['State']['ExitCode'] != 0 or
                            j.container.attrs['State']['OOMKilled']
                    )
            )
        ]

    def get_reserved_mem(self):
        return sum([
            j.mem_limit
            for j in self.get_running_jobs()
        ])

    def update_containers(self):
        for j in self.jobs:
            if j.container is not None:
                j.container.reload()

    def can_run_job(self, job):
        if len(self.get_running_jobs()) >= self.concurrency:
            return False
        mem_req = self.get_reserved_mem() + job.next_mem_limit()
        if mem_req > self.get_free_mem():
            return False
        return True

    def update(self):
        self.update_containers()
        new_run = 0
        # Start pending jobs
        for j in self.get_pending_jobs():
            if self.can_run_job(j):
                # Start job
                print(f'Run {j.file} with {j.next_mem_limit()}G RAM')
                j.run()
                new_run += 1
            elif self.concurrency <= len(self.get_running_jobs()):
                break
            else:
                print(f'No resources for {j.file} with {j.next_mem_limit()}G RAM', file=sys.stderr)
        # Restart failed jobs
        for j in self.get_failed_jobs():
            if self.can_run_job(j):
                # Start job
                print(f'Run {j.file} with {j.next_mem_limit()}G RAM')
                j.run()
                new_run += 1
            elif self.concurrency <= len(self.get_running_jobs()):
                break
            else:
                print(f'No resources for {j.file} with {j.next_mem_limit()}G RAM', file=sys.stderr)
        return new_run