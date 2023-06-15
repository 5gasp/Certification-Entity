import os
import connexion
import six
from flask import render_template, request, send_file, send_from_directory, Response

from .__init__ import logger, mRedis
from swagger_server import cert_entity as cert
from swagger_server import constants as c
from swagger_server import util
from swagger_server.models.cert_created import CertCreated  # noqa: E501
from swagger_server.models.create_cert import CreateCert  # noqa: E501
from swagger_server.models.server_info import ServerInfo  # noqa: E501

# get location variable
API_CERTIFICATE_ENDPOINT = os.environ.get('API_CERTIFICATE_ENDPOINT')


def create_cert(body):  # noqa: E501
    """Create a certificate for a testing (identified by the test_id)

     # noqa: E501

    :param body: Create a certificate
    :type body: dict | bytes

    :rtype: CertCreated
    """
    if connexion.request.is_json:
        body = CreateCert.from_dict(connexion.request.get_json())  # noqa: E501
        if mRedis.exists(body.test_id):
            if int(mRedis.get(f"{body.test_id}_status").decode()) == c.status_finished:
                # API_CERTIFICATE_ENDPOINT overrides the base url
                url = f"{API_CERTIFICATE_ENDPOINT or request.base_url}?test_id={body.test_id}&access_token={body.access_token}"
                return {"message":"The certificate for this ID has already been created.", "certificate": url}, 208
            elif int(mRedis.get(f"{body.test_id}_status").decode()) == c.status_progress:
                return "This certificate is currently being created, please wait.", 208

        msg_prefix = f"test_id '{body.test_id}'"
        logger.info(f"{msg_prefix}: Start creating certificate")

        # Redis
        mRedis.set(body.test_id, "")
        mRedis.set(f"{body.test_id}_access_token", body.access_token)
        mRedis.set(f"{body.test_id}_status", c.status_progress)
        
        
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
                # Redis
                mRedis.set(f"{body.test_id}_status", c.status_error)
                return output, 404
            elif output:
                radar_chart, cert_file = output                
                # Redis
                mRedis.set(f"{body.test_id}_access_token", body.access_token)
                mRedis.set(f"{body.test_id}_status", c.status_finished)
                mRedis.set(f"{body.test_id}_cert", f'{cert_file}.pdf')
                mRedis.set(f"{body.test_id}_chart", radar_chart)
                
                # API_CERTIFICATE_ENDPOINT overrides the base url
                url = f"{API_CERTIFICATE_ENDPOINT or request.base_url}?test_id={body.test_id}&access_token={body.access_token}"
                return {'certificate': url}, 200
               
            else:
                mRedis.set(f"{body.test_id}_status", c.status_finished_no_cert)
                return ("Request has been executed, but the certificate will not be created. "
                        "The minimum grade of bronze was not achieved."), 200
        else:
            all_err_msg = ' '.join([err_msg_1, err_msg_2, err_msg_3])
            mRedis.set(f"{body.test_id}_status", c.status_error)
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
    if mRedis.exists(test_id) and int(mRedis.get(f"{test_id}_status").decode()) == c.status_finished:
        if access_token == mRedis.get(f"{test_id}_access_token").decode():
            pdf_file = mRedis.get(f"{test_id}_cert").decode() 
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
