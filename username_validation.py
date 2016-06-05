import tool_labs_utils
from pypodio2 import api
from client_settings import *


def main(event_checkin_app=14347171, user_manifest_app=14347585, checkin_username_field=109820693, manifest_username_field=109823938,
         associated_user_profile=109824325, associated_event_profile=109850232):
    sql = tool_labs_utils.WMFReplica()  # usage: sql.query(...)
    c = api.OAuthClient(client_id,client_secret,username,password)
    checkins = c.transport.POST('item', 'app', event_checkin_app, 'filter', filters={associated_user_profile: [None]}, limit=500)['items']
    manifest = c.Application.get_items(user_manifest_app, limit=500)['items']

    user_profiles = {}

    # Prepare a manifest dictionary `user_profiles`
    for item in manifest:
        item_id = item['item_id']
        extant_fields = {field['field_id']: list(field['values'][0].values()) for field in item['fields']}
        username = extant_fields[manifest_username_field][0]
        user_profiles[username] = item_id

    print("Loaded " + str(len(user_profiles)) + " user profiles")

    # Now going through and checking for matches against `user_profiles`
    for item in checkins:
        item_id = item['item_id']
        extant_fields = {field['field_id']: list(field['values'][0].values()) for field in item['fields']}
        username = extant_fields[checkin_username_field][0]
        username = username[0].upper() + username[1:]
        username = username.replace('_', ' ')
        print("Processing check-in: " + username)

        if username in user_profiles:
            print("Match identified for " + username)
            attributes = {'fields': [{'field_id': associated_user_profile, 'values': [{'value': user_profiles[username]}]}]}
            print(c.Item.update(item, attributes))