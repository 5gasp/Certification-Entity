"""
5GASP Certification Entity
"""
import os
import string
from datetime import date, datetime, timedelta

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


def _build_base_dictionary(base_info, results, test_cases, cert_tc_list):
    """Check for the required data in the responses from the CI/CD Manager.
    Only keep the test results of test cases required for the certification (based on the app's selected conditions).
    Build the base dictionary with this structure:
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
    :param test_cases: general test case info
    :type test_cases: dict
    :param cert_tc_list: list of tests required for certification
    :type cert_tc_list: list[str]

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
    for test in cert_tc_list:
        info = test_cases.get(test, {})
        # Sort test cases into groups based on axis
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
            'name': info.get('name', ''),
            'weight': weight,
            'mandatory': mandatory,
            'results': [],
            'start_time': '',
        }
        tmp_dict = base_dict.get(axis, {})
        tmp_dict.update({test: tc_info})
        base_dict.update({axis: tmp_dict})

    all_timestamps = []
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
        else:
            all_timestamps.append(start_time)
        tc_id = test.get('original_test_name')
        if not tc_id:
            err_msg.append(msg_result.format(performed, 'original_test_name', tc_id))
        else:
            tc = test_cases.get(tc_id)
            # Save result if test is required for certification
            if tc and tc_id in cert_tc_list:
                axis = tc.get('axis')
                tmp_dict = base_dict.get(axis, {}).get(tc_id, {})
                tmp_dict['start_time'] = start_time
                tmp_result = tmp_dict.get('results', [])
                tmp_result.append(tc_result)
            elif not tc:
                err_msg.append(f"Could not find test '{tc_id}' in test case database (/tests/all).")

    # Automatically pass selected onboarding tests
    timestamps = [datetime.strptime(x, c.cicd_date_format) for x in all_timestamps]
    timestamps.sort()
    onboard_time = timestamps[0] if timestamps else ''
    if onboard_time:
        onboard_time = onboard_time - timedelta(minutes=c.onboard_time_offset)
        onboard_time = onboard_time.strftime(c.cicd_date_format)
    for tc_id in c.onboarding_tests:
        tc = test_cases.get(tc_id)
        axis = tc.get('axis')
        tmp_dict = base_dict.get(axis, {}).get(tc_id, {})
        tmp_dict['start_time'] = onboard_time
        tmp_dict['results'] = [True]

    return base_dict, ' '.join(err_msg)


def _calculate_axis_scores(base_dict):
    """Calculate the score for each axis and return as dictionary. The score is calculated in the following way:
    A) If all mandatory tests are passed, the result is 1, otherwise it is 0.
    B) Calculate the weighted average for the executed conditional tests.
    To get the final axis score, multiply A and B.
    If no mandatory test exists and no conditional test was applied for an axis,
    set -1 to indicate that this axis can be ignored for grading.

    :param base_dict: dictionary from _build_base_dictionary()
    :type base_dict: dict

    :return: dictionary of axis scores, dictionary of minimum requirements
    :rtype: (dict, dict)
    """
    logger.debug("Calculate axis scores")
    axis_scores = {}
    min_req = {}
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

        # No required tests, set axis score to -1
        logger.debug(f"--- Axis: {axis}, mandatory tests number: {m_num_passed}/{m_num_tests}, "
                     f"conditional test weights: {o_result_sum}/{o_weight_sum}")
        if m_num_tests == 0 and o_weight_sum == 0:
            axis_scores.update({axis: -1})
        else:
            m_score = c.weight_mandatory if m_num_tests == m_num_passed else 0
            o_score = (o_result_sum / o_weight_sum) * c.weight_optional if o_result_sum else 1
            axis_scores.update({axis: m_score * o_score})
        min_req.update({axis: c.weight_mandatory if m_num_tests else 0})
    return axis_scores, min_req


def _create_radar_chart(axis_scores, filename, show_min=None):
    """Plot a radar chart with the given scores.
    https://www.pythoncharts.com/matplotlib/radar-charts/

    :param axis_scores: dictionary of axis scores
    :type axis_scores: dict
    :param filename: filename for the chart
    :type filename: str
    :param show_min: dictionary for drawing minimum requirements in the chart
    :type show_min: dict
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
        min_values = [show_min.get(x, 0) for x in axis_scores.keys()]
        min_values.append(min_values[0])
        ax.plot(draw_angles, min_values, color='orange', linewidth=1, label='Minimum requirements')
        ax.fill(draw_angles, min_values, color='orange', alpha=0.25)
    # Draw scores
    draw_m_values = [x if x >= 0 else 0 for x in scores]
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
    achieved, create a document with the intermediary results.

    :param base_dict: dictionary from _build_base_dictionary()
    :type base_dict: dict
    :param axis_scores: score dictionary from _calculate_axis_scores()
    :type axis_scores: dict
    :param base_info: basic info about the testing
    :type base_info: dict
    :param chart_file: filename of the chart to include
    :type chart_file: str
    :param filename: base filename for the document
    :type filename: path-like

    :return: True if document is certificate, else False (intermediary result) and filename of the document
    :rtype: bool, str
    """
    msg_prefix = f"test_id '{base_info['test_id']}'"
    logger.debug(f"{msg_prefix}: Start creating certificate with scores: {axis_scores}")
    # Determine grade (if score is -1, ignore this axis for grading)
    gold = [True if v >= c.score_gold or v == -1 else False for k, v in axis_scores.items()]
    silver = [True if v >= c.score_silver or v == -1 else False for k, v in axis_scores.items()]
    bronze = [True if v >= c.score_bronze or v == -1 else False for k, v in axis_scores.items()]
    if all(gold):
        grade = c.grade_gold
    elif all(silver):
        grade = c.grade_silver
    elif all(bronze):
        grade = c.grade_bronze
    else:
        grade = ""

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
                info['name'],
                'Mandatory' if is_mandatory else 'Conditional',
                test_bed,
                result,
                colour=colour,
            )
            rows.append(row)

    current_date = date.today().strftime(c.sign_date_format)
    tc_link = f"{c.cicd_service_page}?test_id={base_info['test_id']}&access_token={base_info['access_token']}"
    if grade:
        template_file = c.cert_template
        doc_type = 'Certificate'
        is_cert = True
        doc_filename = f'certificate_{filename}'
    else:
        template_file = c.cert_failed_template
        is_cert = False
        doc_type = 'Intermediary result'
        doc_filename = f'result_{filename}'

    with open(template_file, 'r', encoding='utf-8') as f:
        template = string.Template(f.read())
    # Generate certificate part for test conditions
    condition_names = [c.test_conditions.get(x, 'Undefined') for x in base_info['test_conditions']]
    condition_str = [f'<i>{x}</i><br>' for x in sorted(condition_names)]
    has_conditions = f"""\
<p>Under the test conditions</p>
<ul>{''.join(condition_str)}</ul>
"""
    no_conditions = "<p>With no selected test conditions</p>"
    cert = template.substitute(
        grade=grade,
        app_name=base_info['app_name'],
        app_version=base_info['app_version'],
        author=base_info['app_author'],
        conditions=has_conditions if base_info['test_conditions'] else no_conditions,
        chart=chart_file,
        test_cases=''.join(rows),
        tc_link=Markup(tc_link),
        env_info=Markup(base_info['service_order']),
        sign_date=current_date,
    )
    file = os.path.join(c.cert_files_dir, f'{doc_filename}.html')
    with open(file, 'w', encoding='utf-8') as f:
        f.write(cert)
    logger.debug(f"{msg_prefix}: {doc_type} created")
    return is_cert, doc_filename


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


def get_test_conditions(results, test_data, test_bed):
    """Get the selected test conditions by checking which tests were performed.

    :param results: performed tests
    :type results: list[dict]
    :param test_data: test case info of a test bed
    :type test_data: dict
    :param test_bed: test bed ID
    :type test_bed: str

    :return: list of test conditions
    :rtype: list[int]
    """
    conditions = []
    test_bed_tests = test_data.get('tests', {}).get(test_bed)
    if not test_bed_tests:
        logger.warn(f"No test cases were found for test bed ID '{test_bed}' in data from /tests/all.")
        return []
    for result in results:
        test_id = result.get('original_test_name')
        if test_id == 'developer-defined':
            continue
        test_case = test_bed_tests.get(test_id)
        if test_case:
            conditions.extend(test_case.get('test_conditions', []))
        else:
            logger.warn(f"Test case '{test_id}' not found in test info for test bed '{test_bed}'.")
    return sorted(set(conditions))


def get_test_cases(test_conditions, test_bed):
    """Return a list of test case IDs according to the specified test conditions.

    :param test_conditions: list of test conditions
    :type test_conditions: list[int]
    :param test_bed: test bed ID
    :type test_bed: str

    :return: list of test case IDs and error message if an error occurred
    :rtype: (list[str], str)
    """
    test_cases, err_msg = get_test_info('test_cases', -1, '')
    if test_cases:
        tc_data = test_cases.get('tests', {}).get(test_bed, {})
        if tc_data:
            final_list = []
            if len(test_conditions) == 0:
                final_list = [v.get('id') for k, v in tc_data.items() if v.get('mandatory') is True]
            else:
                conditions_set = set(test_conditions)
                for _, test_data in tc_data.items():
                    if test_data.get('mandatory') is True:
                        final_list.append(test_data.get('id'))
                    else:
                        tc_cond = set(test_data.get('test_conditions', []))
                        if tc_cond and tc_cond.issubset(conditions_set):
                            final_list.append(test_data.get('id'))
            return final_list, ""
        else:
            return [], f"No test cases found for test bed '{test_bed}'."
    else:
        return [], err_msg


def create_certificate(base_info, results, test_cases):
    """Create a certificate for the given testing instance.

    :param base_info: basic info about the testing
    :type base_info: dict
    :param results: test results
    :type results: dict
    :param test_cases: test case info
    :type test_cases: dict

    :return: If successful, return if the document is a certificate and the filenames of radar chart and document.
             Otherwise, return an error message.
    :rtype: (bool, str, str) or str
    """
    cert_tc_list, _ = get_test_cases(base_info['test_conditions'], base_info.get('testbed_id'))
    logger.debug(f"test_id {base_info['test_id']}: Certificate test list: {cert_tc_list}")
    base_dict, err_msg = _build_base_dictionary(base_info, results, test_cases, cert_tc_list)
    if err_msg:
        return err_msg
    scores, m_min_req = _calculate_axis_scores(base_dict)
    radar_chart = f"{base_info['test_id']}_radar_chart.png"
    _create_radar_chart(scores, radar_chart, show_min=m_min_req)
    filename_base = f"{base_info['netapp_id']}_{base_info['app_version']}"
    is_cert, filename = _generate_certificate(base_dict, scores, base_info, radar_chart, filename_base)

    doc_html = os.path.join(c.cert_files_dir, f'{filename}.html')
    doc_pdf = os.path.join(c.cert_files_dir, f'{filename}.pdf')
    if os.path.isfile(doc_html):
        HTML(filename=doc_html).write_pdf(doc_pdf)
        os.remove(doc_html)
        return is_cert, radar_chart, filename
    else:
        return "Unexpected error, could not find the certificate or result file."
