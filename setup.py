import sys
import subprocess
from setuptools import setup, find_packages

# get requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()


# get dev version from git
cmd = subprocess.Popen("git log --oneline | head -1 | awk '{print $1}'", shell=True, stdout=subprocess.PIPE)
out, err = cmd.communicate()
if err:
    print err
    sys.exit(-1)


setup(
    name='daimaduan.com',
    version='2.0-%s' % out.strip(),
    long_description=__doc__,
    url='https://github.com/DoubleCiti/daimaduan.com',
    author='David Xie',
    author_email='david.scriptfan@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=required
)
