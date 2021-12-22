
tags_metadata = [
    {
        "name": "login",
        "description": "Checks if the user is registered with a normal user account. If he is and the password is correct" +
        "then it returns ok in status, otherwise it returns an error status and a message indicating the error (eg: user does not exist)",
    },
    {
        "name": "admin_login",
        "description": "Checks if the user is registered as an admin. If he is and the password is correct" +
        "then it returns ok in status, otherwise it returns an error status and a message indicating the error",
    },
    {
        "name": "create",
        "description": "Tries to create a new normal user account, returns ok if it was created, error if the user already exists or any other error ocurrs",
    },
    {
        "name": "admin_create",
        "description": "Tries to create a new admin account, returns ok if it was created, error if the user already exists or any other error ocurrs",
    },
    {
        "name": "users_list",
        "description": "Returns a list containing the emails and blocking status of all the users from the platform",
    },
    {
        "name": "oauth_login",
        "description": "Checks if the user has a google account, if it already has then it returns ok  and the message: {google account exists}, " + 
        "otherwise if the user did not have a google account it is created, answearing also with an ok status and message {user successfully registered}." + 
        "If the user already has an account it returns an error status with the message {has normal account}",
    },
    {
        "name": "change_blocked_status",
        "description": "Changes the account status of the received user based in the value received in is_blocked, if it is True then the user is blocked" + 
        ", otherwise he is unblocked. Returns an ok status if the process was executed sucessfuly, otherwise it returns an error status with a message",
    },
    {
        "name": "users_metrics",
        "description": "Changes the account status of the received user based in the value received in is_blocked, if it is True then the user is blocked" + 
        ", otherwise he is unblocked. Returns an ok status if the process was executed sucessfuly, otherwise it returns an error status with a message",
    },
    {
        "name": "send_message",
        "description": "Sends an HTTP request to the endpoint that redirects it to the cellphone that has to receive the push notification, it returns" + 
        "allways an ok status",
    },
]