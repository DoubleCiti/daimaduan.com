import sys
import re
import subprocess
from setuptools import setup, find_packages

# get requirements
install_requires = []
dependency_links = []
with open('requirements.txt') as f:
    for line in f.read().splitlines():
        if line.startswith('-e'):
            install_requires.append(re.sub(r'.*egg=', '', line))
            dependency_links.append(re.sub(r'^-e ', '', line))
        else:
            install_requires.append(line)

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
    install_requires=install_requires,
    dependency_links=dependency_links
)
