import json
import requests


class RPCMethod:
    def __init__(self, rpc_method, host):
        self._rpc_method = rpc_method
        self._host = host

    def __getattr__(self, rpc_method):
        new_method = '{}.{}'.format(self._rpc_method, rpc_method)
        return RPCMethod(new_method, self._host)

    def __call__(self, *args):
        __payload = json.dumps({"method": self._rpc_method, "params": list(args), "jsonrpc": "2.0"})
        try:
            response = self._host._session.post(self._host._url, headers=self._host._headers, data=__payload)
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        if response.status_code not in (200, 500):
            raise Exception("RPC connection failure: " + str(response.status_code) + " " + response.reason)
        response_json = response.json()
        if "error" in response_json and response_json["error"] is not None:
            raise Exception("Error in RPC call: " + str(response_json["error"]))
        return response_json["result"]
