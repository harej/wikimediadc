# User Manifest: 14347585
# Account Creation Date Field: 109850343


import arrow
import tool_labs_utils
from pypodio2 import api
from client_settings import *

def main():
    sql = tool_labs_utils.WMFReplica()  # usage: sql.query(...)
    c = api.OAuthClient(client_id,client_secret,username,password)
    manifest = c.Application.get_items(14347585, limit=500)['items']
    
    for item in manifest:
        extant_fields = {field['field_id']: list(field['values'][0].values())
                         for field in item['fields']}
        
        if 109850343 not in extant_fields:  # account creation field not set
            user = extant_fields[109823938][0]
            q = ('select user_registration from user '
                 'where user_name = "{0}"').format(user)
            reg_date = sql.query('enwiki', q, None)[0][0].decode('utf-8')
            reg_date = arrow.get(reg_date, 'YYYYMMDDHHmmss')
            reg_date = reg_date.format('YYYY-MM-DD HH:mm:ss')
            
            attributes = {'fields': [{'field_id': 109850343,
                                     'values': [{'start-utc': reg_date}]}]}


            id = item['item_id']

            print(c.Item.update(id, attributes))

            
main()