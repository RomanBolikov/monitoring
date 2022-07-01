import requests
from concurrent.futures import ThreadPoolExecutor


class Request:
    def __init__(self, date):
        self.date = date
        common_params = {
            'PubDateType': 'single', 'PubDateSingle': date, 'RangeSize': 100
        }

        fz_params = common_params | {
            'SelectedDocumentType': '82a8bf1c-3bc7-47ed-827f-7affd43a7f27'
            }

        president_params = common_params | {
            'SelectedSignatoryAuthorityId':
            '225698f1-cfbc-4e42-9caa-32f9f7403211',
            'SelectedDocumentType': '0790e34b-784b-4372-884e-3282622a24bd'
            }

        pprf_params = common_params | {
            'SelectedSignatoryAuthorityId':
            '8005d8c9-4b6d-48d3-861a-2a37e69fccb3',
            'SelectedDocumentType': 'fd5a8766-f6fd-4ac2-8fd9-66f414d314ac'
            }

        rprf_params = common_params | {
            'SelectedSignatoryAuthorityId':
            '8005d8c9-4b6d-48d3-861a-2a37e69fccb3',
            'SelectedDocumentType': '7ff5b3b5-3757-44f1-bb76-3766cabe3593'
            }

        ksrf_params = common_params | {
            'SelectedSignatoryAuthorityId':
            '72b9c96e-9091-4b4e-b5eb-113a8432d2cd'
            }

        minstroy_params = common_params | {
            'SelectedSignatoryAuthorityId':
            'efa6da4b-4c1a-4fa8-8caf-860c17b205fd',
            'SelectedDocumentType': '2dddb344-d3e2-4785-a899-7aa12bd47b6f'
            }

        self.params = (
            fz_params, president_params, pprf_params, rprf_params,
            ksrf_params, minstroy_params
        )

        self.total_list = self.output()

    def response(self, parameters):
        try:
            res = requests.get(
                'http://publication.pravo.gov.ru/api/Document/Get',
                params=parameters, timeout=1
            )
        except (
            requests.exceptions.Timeout or requests.exceptions.ConnectionError
        ):
            return -1
        return res.json()['Documents']

    def output(self):
        out = []
        with ThreadPoolExecutor(max_workers=6) as exec:
            for result in exec.map(self.response, self.params):
                if result == -1:
                    return None
                out.extend(result)
            return out


if __name__ == '__main__':
    import time
    start = time.monotonic()
    req = Request('14.06.2022')
    print(len(req.total_list))
    finish = time.monotonic() - start
    print(finish)
