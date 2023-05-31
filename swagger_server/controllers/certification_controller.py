import json
import os

import connexion
import six
from flask import render_template, request, send_file

from .__init__ import cert_data, logger
from swagger_server import cert_entity as cert
from swagger_server import constants as c
from swagger_server import util
from swagger_server.models.cert_created import CertCreated  # noqa: E501
from swagger_server.models.create_cert import CreateCert  # noqa: E501
from swagger_server.models.server_info import ServerInfo  # noqa: E501


def _save_database():
    """Save the loaded database. Return True if successful, otherwise False."""
    try:
        with open(c.database, 'w') as f:
            json.dump(cert_data, f)
        logger.debug("Saved database cert_data")
        return True
    except Exception as e:
        logger.error(f"Error occurred while saving the database: {e}")
        return False


def create_cert(body):  # noqa: E501
    """Create a certificate for a testing (identified by the test_id)

     # noqa: E501

    :param body: Create a certificate
    :type body: dict | bytes

    :rtype: CertCreated
    """
    if connexion.request.is_json:
        body = CreateCert.from_dict(connexion.request.get_json())  # noqa: E501
        if body.test_id in cert_data:
            if cert_data[body.test_id]['status'] == c.status_finished:
                return "The certificate for this ID has already been created.", 409
            elif cert_data[body.test_id]['status'] == c.status_progress:
                return "This certificate is currently being created, please wait.", 409

        msg_prefix = f"test_id '{body.test_id}'"
        logger.info(f"{msg_prefix}: Start creating certificate")
        cert_data.update({
            body.test_id: {
                'access_token': body.access_token,
                'status': c.status_progress,
            }
        })
        # Get all required data
        base_info, err_msg_1 = cert.get_test_info('base', body.test_id, body.access_token)
        results, err_msg_2 = cert.get_test_info('results', body.test_id, body.access_token)
        test_cases, err_msg_3 = cert.get_test_info('test_cases', body.test_id, body.access_token)
        if all([base_info, results, test_cases]):
            logger.debug(f"{msg_prefix}: All required info retrieved")
            base_info.update({
                'access_token': body.access_token,
                'app_name': body.app_name,
                'app_version': body.app_version,
                'app_author': body.app_author,
                'service_order': body.service_order,
            })
            # Create certificate
            output = cert.create_certificate(base_info, results, test_cases)
            if isinstance(output, str):
                cert_data[body.test_id]['status'] = c.status_error
                return output, 404
            elif output:
                radar_chart, cert_file = output
                cert_data.update({
                    body.test_id: {
                        'access_token': body.access_token,
                        'status': c.status_finished,
                        'cert': f'{cert_file}.pdf',
                        'chart': radar_chart,
                    }
                })
                ok = _save_database()
                if ok:
                    # Throws werkzeug.routing.exceptions.BuildError, endpoint can't be found
                    # url = url_for('certificate', _method=get_cert, _external=True,
                    #               values={'test_id': body.test_id, 'access_token': body.access_token})
                    url = f"{request.base_url}?test_id={body.test_id}&access_token={body.access_token}"
                    return {'certificate': url}, 200
                else:
                    cert_data[body.test_id]['status'] = c.status_error
                    return "Unexpected error occurred while saving certificate.", 500
            else:
                cert_data[body.test_id]['status'] = c.status_finished_no_cert
                return ("Request has been executed, but the certificate will not be created. "
                        "The minimum grade of bronze was not achieved."), 200
        else:
            all_err_msg = ' '.join([err_msg_1, err_msg_2, err_msg_3])
            cert_data[body.test_id]['status'] = c.status_error
            return (f"Could not fetch all required data from the CI/CD Manager to create the certificate: "
                    f"{all_err_msg}"), 404


def get_cert(test_id, access_token):  # noqa: E501
    """Get the certificate for a testing (identified by the test_id)

     # noqa: E501

    :param test_id:
    :type test_id: int
    :param access_token:
    :type access_token: str

    :rtype: str
    """
    if test_id in cert_data and cert_data[test_id]['status'] == c.status_finished:
        if access_token == cert_data[test_id]['access_token']:
            pdf_file = cert_data[test_id]['cert']
            file_path = os.path.join(c.cert_files_dir, pdf_file)
            return send_file(file_path, as_attachment=True), 200
        else:
            return "The access token is not correct for this ID.", 403
    else:
        return "A certificate for this ID does not exist.", 404


def get_server_info():  # noqa: E501
    """Get server info

     # noqa: E501


    :rtype: ServerInfo
    """
    return {
        'name': c.server_name,
        'version': c.version,
    }
