import arrow
from pypodio2 import api
from client_settings import *
from globalmetrics import GlobalMetrics


# App IDs:
# Event Check-Ins: 14347171

# Field IDs:
# Metrics Consent: 109821228
# Associated User Profile: 109824325
# Associated Event Profile: 109850232
# ~
# (list of) Articles Edited During Event: 109850233
# (list of) Media Files Uploaded: 109850237
# Number of Articles Edited: 109850234
# Number of Edits Made: 109866023
# Number of Bytes Changed: 109850235
# Number of Media Files Uploaded: 109850236
# Report Generated? 110841158


def main():
    # Get all the items
    global_metric_fields = [109850233, 109850237, 109850234, 109866023, 109850235, 109850236]
    c = api.OAuthClient(client_id,client_secret,username,password)
    checkins = c.transport.POST('item', 'app', 14347171, 'filter', filters={110841158: [None]})['items']

    send_to_globalmetrics = {}
    
    for item in checkins:
        checkin_id = item['item_id']
        # Create dictionary to simplify batshit Podio output
        extant_fields = {field['field_id']: list(field['values'][0].values()) \
                         for field in item['fields']}

        # Can we analyze this entry?
        condition1 = (extant_fields[109821228][0]['id'] == 1)  # Metrics consent check
        condition2 = 109824325 in extant_fields \
                     and len(extant_fields[109824325]) > 0  # Associated user
        condition3 = 109850232 in extant_fields \
                     and len(extant_fields[109850232]) > 0  # Assoicated event

        if condition1 and condition2 and condition3:
            # Get canonical username and event date/time range
            user_item = extant_fields[109824325][0]['item_id']
            event_item = extant_fields[109850232][0]['item_id']
            user = None  # Initializing
            date_range = None

            for global_metric_field in global_metric_fields:
                if global_metric_field not in extant_fields \
                or len(extant_fields[global_metric_field]) == 0:
                    # Retrieving username and event date ranges from associated items
                    if user == None:  # To avoid redundant queries
                        user = c.transport.GET('item', user_item,
                                   'value', 109823938)[0]['value']
                        user = user.replace("_", " ")  # normalizing
                        if date_range == None:
                            daterange = c.transport.GET('item', event_item,
                                        'value', 103174438)[0]
                            daterange = [daterange['start_utc'], daterange['end_utc']]
                            daterange = [arrow.get(date, 'YYYY-MM-DD HH:mm:ss')
                                         for date in daterange]

                    # Checking for event being indexed in the dictionary
                    # Initializes it if not
                    if event_item not in send_to_globalmetrics:
                        send_to_globalmetrics[event_item] = \
                        {'start_date': daterange[0], 'end_date': daterange[1],
                         'projects': ['enwiki'],
                         'cohort': []}

                    # Adding username to cohort list
                    send_to_globalmetrics[event_item]['cohort'].append((user, checkin_id))
                    
    for event_item, blob in send_to_globalmetrics.items():
        cohort = [x[0] for x in blob['cohort']]  # only the usernames
        projects =  blob['projects']
        start = blob['start_date']
        end = blob['end_date']
        
        metrics = GlobalMetrics(cohort, projects, start, end)
        newly_registered = metrics.newly_registered['enwiki']
        uploaded_media = metrics.uploaded_media['commonswiki']
        absolute_bytes = metrics.absolute_bytes['enwiki']
        edited_articles_list = metrics.edited_articles_list['enwiki']
        number_of_edits = metrics.number_of_edits['enwiki']
        
        assoc_checkins = {x[0]: x[1] for x in blob['cohort']}
        
        for user, checkin in assoc_checkins.items():
            attributes = {
                            "fields": [
                                        {"field_id": 110841158,  # Report Generated?
                                         "values": [{"value": [1]}]
                                        },
                                        {"field_id": 109850234,  # Number of Articles Edited
                                         "values": [{"value": len(edited_articles_list[user])}]
                                        },
                                        {"field_id": 109866023,  # Number of Edits Made
                                         "values": [{"value": number_of_edits[user]}]
                                        },
                                        {"field_id": 109850235,  # Number of Bytes Changed
                                         "values": [{"value": absolute_bytes[user]}]
                                        },
                                        {"field_id": 109850236,  # Number of Media Files Uploaded
                                         "values": [{"value": len(uploaded_media[user])}]
                                        }
                                      ]
                         }
 
            if len(edited_articles_list[user]) > 0:
                attributes["fields"].append({"field_id": 109850233,  # (list of) Articles Edited During Event
                                             "values": [{"value": "|".join(edited_articles_list[user])}]
                                            }
                                           )
            if len(uploaded_media[user]) > 0:
                attributes["fields"].append({"field_id": 109850237,  # (list of) Media Files Uploaded
                                             "values": [{"value": "|".join(uploaded_media[user])}]
                                            }
                                           )

            print(c.Item.update(checkin, attributes))
            
main()