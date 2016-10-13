from .integration import BaseResourceClient, RelatedResourceBase

class TransactionsAndBillsResource(RelatedResourceBase):

    resource_url = 'billstransactions'


class TransactionsResource(RelatedResourceBase):
    resource_url = 'transactions'


class LiveHistoryResource(RelatedResourceBase):
    resource_url = 'livehistory'


class DemandHistoryResource(RelatedResourceBase):
    resource_url = 'ondemandhistory'


class FlagHistoryResource(RelatedResourceBase):
    resource_url = 'flaghistory'


# Old resource Not Used now
class ChangeHistoryResource(RelatedResourceBase):
    resource_url = 'changehistory'


class UsersResourceClient(BaseResourceClient):

    per_page = 30

    resource_url = 'users'

    def alter_data(self, data):
        destination = {}
        for key, value in data.items():
            keys = key.split(".")
            d = destination
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}    
                d = d[key]

            d[keys[-1]] = value

        return destination


class ChangeBalanceResource(RelatedResourceBase):
    resource_url = 'correct_balance'
