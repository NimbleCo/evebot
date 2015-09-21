import subprocess


def run_command(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait(1)

    out, err = process.communicate()

    return out.decode('utf-8'), err.decode('utf-8'), process.returncode
