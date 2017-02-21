import editathon, registration_date, username_validation

def main():
    U = username_validation()
    R = registration_date()
    E = editathon()

    U.main(event_checkin_app=15908657, user_manifest_app=15908656,
           checkin_username_field=123109864, manifest_username_field=123109855,
           associated_user_profile=123109868, associated_event_profile=123109869)

if __name__ == '__main__':
    main()