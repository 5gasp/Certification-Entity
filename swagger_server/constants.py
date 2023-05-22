import os

# ----------
# Server data
# ----------
server_name = '5GASP Certification Entity'
version = '0.1'
users = {
    # 'username': 'password',
    'testuser': 'arXKcZKv610q9geHqOoZZzEW',
}

# ----------
# Certification
# ----------
cicd_manager_base = 'https://ci-cd-manager.5gasp.eu/manager'
sign_date_format = '%d/%m/%Y'
test_info_link = 'https://5gasp.eu/somelink_to_testcases'

# Test axis numbers
axis_1 = 1
axis_2 = 2
axis_3 = 3
axis_4 = 4
# Test axis names
axis_names = {
    axis_1: '5G Readiness',
    axis_2: 'Security & Privacy',
    axis_3: 'Performance & Scalability',
    axis_4: 'Availability & Continuity',
}

# Certification grades, score can be in range [1, 10]
# The minimum score that must be achieved for each axis to obtain a certain grade.
score_bronze = 1
score_silver = 5
score_gold = 8
grade_bronze = 'Bronze'
grade_silver = 'Silver'
grade_gold = 'Gold'

# Minimum requirements
min_requirements = {
    axis_1: 1,
    axis_2: 1,
    axis_3: 1,
    axis_4: 1,
}

# Colours for test result column
green = '#27ae60'
yellow = '#f1c40f'
red = '#e74c3c'
grey = '#ddd'

# ----------
# Internal
# ----------
# Directories
server_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(server_dir, os.pardir))
cert_files_dir = os.path.join(root_dir, 'cert_files')
log_dir = os.path.join(root_dir, 'logs')
template_dir = os.path.join(cert_files_dir, 'template')
# Files
database = os.path.join(cert_files_dir, 'database.json')
cert_template = os.path.join(template_dir, 'certificate_template.html')
logo_ec = os.path.join(template_dir, 'ec_logo.png')
logo_5gasp = os.path.join(template_dir, '5gasp_logo.png')
log_file = os.path.join(log_dir, 'app_server.log')

# Progress status
status_progress = 1
status_finished = 2
status_error = 3
status_finished_no_cert = 4
status_names = {
    status_progress: 'In progress',
    status_finished: 'Finished',
    status_finished_no_cert: 'Finished without certificate',
    status_error: 'Error',
}

