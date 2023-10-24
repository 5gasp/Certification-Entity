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
cicd_service_page = 'https://ci-cd-service.5gasp.eu/dashboard/test-information.html'

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

# Test conditions
test_conditions = {
    1: 'NEF support',
    2: 'Location-based app',
    3: 'Mobility-based app',
    4: 'Premium QoS app',
    5: 'Deployment type VM',
    6: 'Deployment type Container',
    7: 'Data plane app',
    8: 'Application layer traffic',
    9: 'Scalable on the number of users',
    10: 'Scalable on the number of Network Application instances',
}

# Certification grades, score can be in range [1, 10]
# The minimum score that must be achieved for each axis to obtain a certain grade.
score_bronze = 1
score_silver = 5
score_gold = 8
grade_bronze = 'Bronze'
grade_silver = 'Silver'
grade_gold = 'Gold'

# Weight for category
weight_mandatory = 1
weight_optional = 10
# Minimum requirements
min_requirements = {
    axis_1: weight_mandatory,
    axis_2: weight_mandatory,
    axis_3: weight_mandatory,
    axis_4: weight_mandatory,
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
cert_failed_template = os.path.join(template_dir, 'cert_failed_template.html')
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

