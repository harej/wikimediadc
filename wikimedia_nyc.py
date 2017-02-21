import editathon, registration_date, username_validation

def main():
    EC = 15908657
    UM = 15908656

    username_validation.main(event_checkin_app=EC,
                             user_manifest_app=UM,
                             checkin_username_field=123109864,
                             manifest_username_field=123109855,
                             associated_user_profile=123109868,
                             associated_event_profile=123109869)

    registration_date.main(username_field=123109855,
                           user_manifest=UM,
                           account_creation_date_field=123109856,
                           registration_date_retrieved=140624733)

    editathon.main(app_id=EC,
                   list_of_articles_edited_during_event=123109874,
                   list_of_media_files_uploaded=123109871,
                   number_of_articles_edited=123109873,
                   number_of_edits_made=123109872,
                   number_of_bytes_changed=123109875,
                   number_of_media_files_uploaded=123109870,
                   report_generated=123109877,
                   metrics_consent=123109867,
                   associated_user_profile=123109868,
                   associated_event_profile=123109869,
                   username_field=123109855,
                   event_date=123110084)

if __name__ == '__main__':
    main()
