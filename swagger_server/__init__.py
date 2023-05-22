import errno
import os

from . import constants as c

# Create files if missing
if not os.path.exists(c.cert_files_dir):
    os.makedirs(c.cert_files_dir)
if not os.path.exists(c.template_dir):
    os.mkdir(c.template_dir)
if not os.path.exists(c.log_dir):
    os.mkdir(c.log_dir)
if not os.path.exists(c.database):
    with open(c.database, 'w') as f:
        f.write('{}')

# Verify that the required files for certificate creation are present.
for file in [c.cert_template, c.logo_ec, c.logo_5gasp]:
    if not os.path.exists(c.cert_template):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
