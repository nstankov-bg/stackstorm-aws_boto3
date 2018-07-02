import boto3
from botocore.exceptions import WaiterError

from st2common.runners.base_action import Action


# pylint: disable=too-few-public-methods
class WaiterRunner(Action):
    def run(self, service, region, waiter_name, credentials, params, max_attempts=20):
        success = False
        client = None
        result = dict()
        service_waiter = None

        if 'WaiterConfig' not in params:
            # We should wait no more than 300 seconds
            params['WaiterConfig'] = {'MaxAttempts': max_attempts}

        if credentials is not None:
            session = boto3.Session(
                aws_access_key_id=credentials['Credentials']['AccessKeyId'],
                aws_secret_access_key=credentials['Credentials']['SecretAccessKey'],
                aws_session_token=credentials['Credentials']['SessionToken'])
            client = session.client(service, region_name=region)
        else:
            client = boto3.client(service, region_name=region)

        if client is None:
            return False, 'boto3 client creation failed'

        try:
            service_waiter = client.get_waiter(waiter_name)
        except ValueError, e:
            result['error'] = e.message

        try:
            service_waiter.wait(**params)
        except WaiterError, e:
            result['error'] = e.message
        else:
            success = True

        return success, result
