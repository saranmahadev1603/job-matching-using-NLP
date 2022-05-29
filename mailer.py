from mailjet_rest import Client
import os

def sendEmail(to, message) -> bool: 
    api_key = '908b79a76a100572fe9a7b705b9b6782'
    api_secret = '3845d947835b01980e8ff7c4b4ce18b4'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": "stamilarasu38@gmail.com",
            "Name": "Tamil Arasu"
        },
        "To": [
            {
            "Email": to,
            "Name": "Applicant"
            }
        ],
        "Subject": "You have been shortlisted",
        "TextPart": "Congratulations!",
        "HTMLPart": "<h3>You Have Been Successfully Selected!</h3><br><p>"+ message+"</p>",
        "CustomID": "SelectedSuccessFully"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    
    if result.json()["Messages"][0]["Status"] == "success":
        return True
    else:
        return False
    
