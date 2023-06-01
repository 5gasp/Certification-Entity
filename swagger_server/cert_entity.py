"""
5GASP Certification Entity
"""
import os
import string
from datetime import date

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
import requests.exceptions
from flask import Markup
from weasyprint import HTML

from swagger_server import constants as c
from swagger_server.controllers.__init__ import logger


def _get_testbed_name(id_):
    url = 'https://ci-cd-manager.5gasp.eu/manager/testbeds/all'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            payload = response.json()
            for testbed in payload['data']['testbeds']:
                if testbed['id'] == id_:
                    return testbed['name']
        else:
            pass
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.error(f"Cannot connect to CI/CD Manager: {e}")
    except Exception:
        pass
    return id_


def _build_base_dictionary(base_info, results, test_cases):
    """Check for the required data in the responses from the CI/CD Manager. Build the base dictionary with this
    structure:
    axis:
        test_case:
            weight: int
            mandatory: bool
            results: list
            start_time: str
        test_case:
            ...
    axis:
        ...

    :param base_info: basic info about the testing
    :type base_info: dict
    :param results: test results
    :type results: dict
    :param test_cases: test case info
    :type test_cases: dict

    :return: base dictionary, error message
    :rtype: dict, str
    """
    test_bed = base_info.get('testbed_id')
    if not test_bed:
        return {}, ("Could not find the key 'testbed_id' in test base information from CI/CD Manager "
                    "(/gui/test-base-information) or it was empty.")
    test_cases = test_cases.get('tests')
    if not test_cases:
        return {}, "Could not find the key 'tests' in test case data from CI/CD Manager (/tests/all) or it was empty."
    test_cases = test_cases.get(test_bed)
    if not test_cases:
        return {}, f"Could not find tests for '{test_bed}' in test case data from CI/CD Manager (/tests/all)."

    base_dict = {
        c.axis_1: {},
        c.axis_2: {},
        c.axis_3: {},
        c.axis_4: {},
    }
    err_msg = []
    msg_tc = "For test case '{0}': Could not find the key '{1}' or its value '{2}' is invalid."
    for test, info in test_cases.items():
        axis = info.get('axis')
        if axis not in c.axis_names:
            err_msg.append(msg_tc.format(test, 'axis', axis))
        weight = info.get('weight')
        if not isinstance(weight, int) and 1 <= weight <= 10:
            err_msg.append(msg_tc.format(test, 'weight', weight))
        mandatory = info.get('mandatory')
        if not isinstance(mandatory, bool):
            err_msg.append(msg_tc.format(test, 'mandatory', mandatory))
        tc_info = {
            'weight': weight,
            'mandatory': mandatory,
            'results': [],
            'start_time': '',
        }
        tmp_dict = base_dict.get(axis, {})
        tmp_dict.update({test: tc_info})
        base_dict.update({axis: tmp_dict})

    msg_result = "For test result '{0}': Could not find the key '{1}' or its value '{2}' is invalid."
    for test in results:
        if test.get('is_developer_defined'):
            continue
        performed = test.get('performed_test', '')
        tc_result = test.get('success')
        if not isinstance(tc_result, bool):
            err_msg.append(msg_result.format(performed, 'success', tc_result))
        start_time = test.get('start_time')
        if not start_time:
            err_msg.append(msg_result.format(performed, 'start_time', start_time))
        tc_id = test.get('original_test_name')
        if not tc_id:
            err_msg.append(msg_result.format(performed, 'original_test_name', tc_id))
        else:
            tc = test_cases.get(tc_id)
            if tc:
                axis = tc.get('axis')
                tmp_dict = base_dict.get(axis, {}).get(tc_id, {})
                tmp_dict['start_time'] = start_time
                tmp_result = tmp_dict.get('results', [])
                tmp_result.append(tc_result)
            else:
                err_msg.append(f"Could not find test '{tc_id}' in test case database (/tests/all).")

    return base_dict, ' '.join(err_msg)


def _calculate_axis_scores(base_dict):
    """Calculate the score for each axis and return as dictionary. The score is calculated in the following way:
    A) If all mandatory tests are passed, the result is 1, otherwise it is 0.
    B) Calculate the weighted average for the executed optional tests.
    To get the final axis score, multiply A and B.

    :param base_dict: dictionary from _build_base_dictionary()
    :type base_dict: dict

    :return: dictionary of axis scores
    :rtype: dict
    """
    logger.debug("Calculate axis scores")
    axis_scores = {}
    for axis, tests in base_dict.items():
        m_num_tests = 0
        m_num_passed = 0
        o_result_sum = 0
        o_weight_sum = 0
        for tc_id, info in tests.items():
            is_mandatory = info['mandatory']
            if is_mandatory:
                m_num_tests += 1
            else:
                o_weight_sum = o_weight_sum + info['weight']
            if len(info['results']) == 0:
                continue
            tc_result = all(info['results'])  # Combine sub test results
            if tc_result:
                if is_mandatory:
                    m_num_passed += 1
                else:
                    o_result_sum = o_result_sum + info['weight']

        m_score = 1 if m_num_tests and m_num_tests == m_num_passed else 0
        o_score = (o_result_sum / o_weight_sum) * 10 if o_result_sum else 1
        axis_scores.update({axis: m_score * o_score})
    return axis_scores


def _create_radar_chart(axis_scores, filename, show_min=True):
    """Plot a radar chart with the given scores.
    https://www.pythoncharts.com/matplotlib/radar-charts/

    :param axis_scores: dictionary of axis scores
    :type axis_scores: dict
    :param filename: filename for the chart
    :type filename: str
    :param show_min: set True to draw minimum requirements in the chart
    :type show_min: bool
    """
    logger.debug(f"Create radar chart '{filename}'")
    matplotlib.use('Agg')  # non-interactive backend

    labels = []
    scores = []
    for axis, score in axis_scores.items():
        labels.append(c.axis_names[axis])
        scores.append(score)
    num_vars = len(labels)
    # Split the circle into even parts and save the angles.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    draw_angles = angles[:]
    draw_angles.append(angles[0])
    # Draw minimum requirements
    if show_min:
        min_values = [c.min_requirements.get(x, 0) for x in axis_scores.keys()]
        min_values.append(min_values[0])
        ax.plot(draw_angles, min_values, color='orange', linewidth=1, label='Minimum requirements')
        ax.fill(draw_angles, min_values, color='orange', alpha=0.25)
    # Draw scores
    draw_m_values = scores[:]
    draw_m_values.append(scores[0])
    ax.plot(draw_angles, draw_m_values, color='blue', linewidth=2, label='Achieved score')
    ax.fill(draw_angles, draw_m_values, color='blue', alpha=0.25)
    # Create legend
    ax.legend(bbox_to_anchor=(1, 0, 0.8, 1))
    # Fix axis to go in the right order and start at 12 o'clock.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    # Draw axis lines for each angle and label.
    ax.set_thetagrids(np.degrees(angles), labels)

    # Go through labels and adjust alignment based on where it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')
    # Ensure radar goes from 0 to 10.
    ax.set_ylim(0, 10)
    # Set position of y-labels (0-10) to be in the middle of the first two axes.
    ax.set_rlabel_position(180 / num_vars)
    # Make the y-axis (0-100) labels smaller.
    ax.tick_params(axis='y', labelsize=9)

    # Save plot as PNG file.
    file = os.path.join(c.cert_files_dir, filename)
    fig.savefig(file, bbox_inches='tight')
    logger.debug(f"Created radar chart '{filename}'")


def _generate_certificate(base_dict, axis_scores, base_info, chart_file, filename):
    """Generate a certificate based on the axis scores and grading definition. If the minimum grade of bronze is not
    achieved, do not create certificate.

    :param base_dict: dictionary from _build_base_dictionary()
    :type base_dict: dict
    :param axis_scores: dictionary from _calculate_axis_scores()
    :type axis_scores: dict
    :param base_info: basic info about the testing
    :type base_info: dict
    :param chart_file: filename of the chart to include
    :type chart_file: str
    :param filename: filename for the certificate
    :type filename: path-like

    :return: True if created else False
    :rtype: bool
    """
    msg_prefix = f"test_id '{base_info['test_id']}'"
    logger.debug(f"{msg_prefix}: Start creating certificate with scores: {axis_scores}")
    # Determine grade
    gold = [True for k, v in axis_scores.items() if v >= c.score_gold]
    silver = [True for k, v in axis_scores.items() if v >= c.score_silver]
    bronze = [True for k, v in axis_scores.items() if v >= c.score_bronze]
    if len(gold) > 0 and all(gold):
        grade = c.grade_gold
    elif len(silver) > 0 and all(silver):
        grade = c.grade_silver
    elif len(bronze) > 0 and all(bronze):
        grade = c.grade_bronze
    else:
        grade = ""
        # return False

    # Create test case table entries
    test_bed = _get_testbed_name(base_info['testbed_id'])
    row_format = """\
<tr>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td>{4}</td>
    <td style="background-color:{colour}">{5}</td>
</tr>
"""
    rows = []
    for axis, tests in base_dict.items():
        for test, info in tests.items():
            is_mandatory = info['mandatory']
            # Skip optional tests that were not executed
            if len(info['results']) == 0 and not is_mandatory:
                continue
            if len(info['results']) == 0:
                result = 'Not tested'
                colour = c.grey
            elif all(info['results']):
                result = 'Passed'
                colour = c.green
            else:
                result = 'Failed'
                colour = c.red
            row = row_format.format(
                info['start_time'],
                c.axis_names[axis],
                test,
                'Mandatory' if is_mandatory else 'Optional',
                test_bed,
                result,
                colour=colour,
            )
            rows.append(row)

    current_date = date.today().strftime(c.sign_date_format)
    tc_link = f"{c.cicd_service_page}?test_id={base_info['test_id']}&access_token={base_info['access_token']}"
    with open(c.cert_template, 'r') as f:
        template = string.Template(f.read())
    cert = template.substitute(
        grade=grade,
        app_name=base_info['app_name'],
        app_version=base_info['app_version'],
        author=base_info['app_author'],
        chart=chart_file,
        test_cases=''.join(rows),
        tc_link=Markup(tc_link),
        env_info=Markup(base_info['service_order']),
        sign_date=current_date,
    )
    file = os.path.join(c.cert_files_dir, filename)
    with open(file, 'w') as f:
        f.write(cert)
    logger.debug(f"{msg_prefix}: Certificate created")
    return True


def get_test_info(info_type, test_id, access_token):
    """Query data from the CI/CD Manager.

    :param info_type: the type of data to query, one of: base, results, test_cases
    :type info_type: str
    :param test_id:
    :type test_id: int
    :param access_token:
    :type access_token: str

    :return: data dictionary, error message
    :rtype: dict, str
    """
    params = {
        'test_id': test_id,
        'access_token': access_token,
    }
    if info_type == 'base':
        uri = '/gui/test-base-information'
        params = params
    elif info_type == 'results':
        uri = '/gui/tests-performed'
        params = params
    elif info_type == 'test_cases':
        uri = '/tests/all'
        params = {}
    else:
        return {}, "Unknown info type"
    msg_prefix = f"test_id '{test_id}' with '{uri}'"

    logger.debug(f"{msg_prefix}: Get data")
    try:
        response = requests.get(f'{c.cicd_manager_base}{uri}', params=params)
        if response.status_code == 200:
            payload = response.json()
            logger.debug(f"{msg_prefix}: Received data: {payload}")
            data = payload.get('data')
            return data, ""
        else:
            err_msg = f"Could not get data from CI/CD Manager: <{response.status_code}> {response.text}."
            logger.error(f"{msg_prefix}: {err_msg}")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        err_msg = "Cannot connect to CI/CD Manager."
        logger.error(f"{err_msg}: {e}")
    except requests.exceptions.JSONDecodeError as e:
        err_msg = f"Response from {uri} could not be JSON decoded."
        logger.error(f"{err_msg}: {e}")
    return {}, err_msg


def create_certificate(base_info, results, test_cases):
    """Create a certificate for the given testing instance.

    :param base_info: basic info about the testing
    :type base_info: dict
    :param results: test results
    :type results: dict
    :param test_cases: test case info
    :type test_cases: dict

    :return: If successful, return filenames of radar chart and certificate file. Otherwise, return an error message.
    :rtype: (str, str) or str or None
    """
    base_dict, err_msg = _build_base_dictionary(base_info, results, test_cases)
    if err_msg:
        return err_msg
    scores = _calculate_axis_scores(base_dict)
    radar_chart = f"{base_info['test_id']}_radar_chart.png"
    _create_radar_chart(scores, radar_chart)
    cert_filename = f"certificate_{base_info['netapp_id']}_{base_info['app_version']}"
    cert_html = os.path.join(c.cert_files_dir, f'{cert_filename}.html')
    cert_pdf = os.path.join(c.cert_files_dir, f'{cert_filename}.pdf')
    ok = _generate_certificate(base_dict, scores, base_info, radar_chart, cert_html)
    if ok:
        HTML(filename=cert_html).write_pdf(cert_pdf)
        os.remove(cert_html)
        return radar_chart, cert_filename
    else:
        return None
