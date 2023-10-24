# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class TestCaseList(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, test_cases: List[int]=None):  # noqa: E501
        """TestCaseList - a model defined in Swagger

        :param test_cases: The test_cases of this TestCaseList.  # noqa: E501
        :type test_cases: List[int]
        """
        self.swagger_types = {
            'test_cases': List[int]
        }

        self.attribute_map = {
            'test_cases': 'test_cases'
        }
        self._test_cases = test_cases

    @classmethod
    def from_dict(cls, dikt) -> 'TestCaseList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The TestCaseList of this TestCaseList.  # noqa: E501
        :rtype: TestCaseList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def test_cases(self) -> List[int]:
        """Gets the test_cases of this TestCaseList.

        List of test case IDs  # noqa: E501

        :return: The test_cases of this TestCaseList.
        :rtype: List[int]
        """
        return self._test_cases

    @test_cases.setter
    def test_cases(self, test_cases: List[int]):
        """Sets the test_cases of this TestCaseList.

        List of test case IDs  # noqa: E501

        :param test_cases: The test_cases of this TestCaseList.
        :type test_cases: List[int]
        """

        self._test_cases = test_cases