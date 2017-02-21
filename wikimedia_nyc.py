import editathon, registration_date, username_validation

def main():
    UM = 15908656

    username_validation.main(event_checkin_app=15908657, user_manifest_app=UM,
           checkin_username_field=123109864, manifest_username_field=123109855,
           associated_user_profile=123109868, associated_event_profile=123109869)

    registration_date.main(username_field=123109855, user_manifest=UM,
                           account_creation_date_field=123109856)

if __name__ == '__main__':
    main()
