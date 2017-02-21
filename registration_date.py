import arrow
import tool_labs_utils
from pypodio2 import api
from client_settings import *

def main(username_field=109823938, user_manifest=14347585, account_creation_date_field=109850343):
    sql = tool_labs_utils.WMFReplica()  # usage: sql.query(...)
    c = api.OAuthClient(client_id,client_secret,username,password)
    manifest = c.Application.get_items(user_manifest, limit=500)['items']
    
    for item in manifest:
        extant_fields = {field['field_id']: list(field['values'][0].values())
                         for field in item['fields']}
        
        if account_creation_date_field not in extant_fields:  # account creation field not set
            user = extant_fields[username_field][0]
            q = ('select user_registration from user '
                 'where user_name = "{0}"').format(user)
            try:
                reg_date = sql.query('enwiki', q, None)[0][0]
            except:
                continue
            
            if reg_date == None:
                reg_date = '1970-01-01 00:00:00'
            else:
                reg_date = reg_date.decode('utf-8')
                reg_date = arrow.get(reg_date, 'YYYYMMDDHHmmss')
                reg_date = reg_date.format('YYYY-MM-DD HH:mm:ss')
            
            attributes = {'fields': [{'field_id': account_creation_date_field,
                                     'values': [{'start_utc': reg_date}]}]}

            id = item['item_id']

            print(c.Item.update(id, attributes))


if __name__ == "__main__":          
    main()
