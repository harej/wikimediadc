import arrow
from pypodio2 import api
from client_settings import *
from globalmetrics import GlobalMetrics


def main(app_id=14347171, list_of_articles_edited_during_event=109850233, list_of_media_files_uploaded=109850237, number_of_articles_edited=109850234,
         number_of_edits_made=109866023, number_of_bytes_changed=109850235, number_of_media_files_uploaded=109850236, report_generated=110841158,
         metrics_consent=109821228, associated_user_profile=109824325, associated_event_profile=109850232, username_field=109823938, event_date=103174438):
    # Get all the items
    global_metric_fields = [list_of_articles_edited_during_event, list_of_media_files_uploaded, number_of_articles_edited,
                            number_of_edits_made, number_of_bytes_changed, number_of_media_files_uploaded]
    c = api.OAuthClient(client_id,client_secret,username,password)
    checkins = c.transport.POST('item', 'app', app_id, 'filter', filters={report_generated: [None], metrics_consent: [1]}, limit=500)['items']

    send_to_globalmetrics = {}
    
    for item in checkins:
        checkin_id = item['item_id']
        # Create dictionary to simplify batshit Podio output
        extant_fields = {field['field_id']: list(field['values'][0].values()) \
                         for field in item['fields']}

        # Can we analyze this entry?
        condition1 = (extant_fields[metrics_consent][0]['id'] == 1)  # Metrics consent check
        condition2 = associated_user_profile in extant_fields \
                     and len(extant_fields[associated_user_profile]) > 0  # Associated user
        condition3 = associated_event_profile in extant_fields \
                     and len(extant_fields[associated_event_profile]) > 0  # Assoicated event

        if condition1 and condition2 and condition3:
            # Get canonical username and event date/time range
            user_item = extant_fields[associated_user_profile][0]['item_id']
            event_item = extant_fields[associated_event_profile][0]['item_id']
            user = None  # Initializing
            date_range = None

            for global_metric_field in global_metric_fields:
                if global_metric_field not in extant_fields \
                or len(extant_fields[global_metric_field]) == 0:
                    # Retrieving username and event date ranges from associated items
                    if user == None:  # To avoid redundant queries
                        user = c.transport.GET('item', user_item,
                                   'value', username_field)[0]['value']
                        user = user.replace("_", " ")  # normalizing
                        if date_range == None:
                            daterange = c.transport.GET('item', event_item,
                                        'value', event_date)[0]
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
                                        {"field_id": report_generated,  # Report Generated?
                                         "values": [{"value": 1}]
                                        },
                                        {"field_id": number_of_articles_edited,  # Number of Articles Edited
                                         "values": [{"value": len(edited_articles_list[user])}]
                                        },
                                        {"field_id": number_of_edits_made,  # Number of Edits Made
                                         "values": [{"value": number_of_edits[user]}]
                                        },
                                        {"field_id": number_of_bytes_changed,  # Number of Bytes Changed
                                         "values": [{"value": absolute_bytes[user]}]
                                        },
                                        {"field_id": number_of_media_files_uploaded,  # Number of Media Files Uploaded
                                         "values": [{"value": len(uploaded_media[user])}]
                                        }
                                      ]
                         }
 
            if len(edited_articles_list[user]) > 0:
                attributes["fields"].append({"field_id": list_of_articles_edited_during_event,  # (list of) Articles Edited During Event
                                             "values": [{"value": "|".join(edited_articles_list[user])}]
                                            }
                                           )
            if len(uploaded_media[user]) > 0:
                attributes["fields"].append({"field_id": list_of_media_files_uploaded,  # (list of) Media Files Uploaded
                                             "values": [{"value": "|".join(uploaded_media[user])}]
                                            }
                                           )

            print(c.Item.update(checkin, attributes))


if __name__ == "__main__":            
  main()