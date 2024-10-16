import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheets:
    def __init__(self, scope, creds, name_table, worksheet):
        self._scope = scope
        self._creds = ServiceAccountCredentials.from_json_keyfile_name(creds, scope)
        self._client = gspread.authorize(self._creds)
        self.sheet = self._client.open(name_table).get_worksheet(worksheet)
