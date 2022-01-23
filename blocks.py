
# Message blocks
start_message = [{
    "type": "section",
	"text": {
		"type": "mrkdwn",
		"text": "Hello, I am Meraki Console Bot. I can help to manage your Meraki cameras to get the live shapshot.\n"
	}
},
{
	"type": "divider"
},
{
	"type": "section",
	"text": {
		"type": "mrkdwn",
		"text": "Please prepare a serial of meraki camera. Click the button below to fill in a form."
	}
},
{
	"type": "actions",
	"elements": [
		{
			"type": "button",
			"text": {
				"type": "plain_text",
				"text": "Start",
				"emoji": True
			},
			"style": "primary",
			"value": "start-button",
			"action_id": "start-button"
		}
	]
}]

camera_modal = {
    "type": "modal",
    "callback_id": "camera_modal",
    "title": {
        "type": "plain_text",
        "text": "Meraki Device Serials"
    },
    "submit": {
        "type": "plain_text",
        "text": "Submit"
    },
    "blocks": [{
    	"type": "input",
    	"block_id": "camera_serial",
    	"label": {
    		"type": "plain_text",
    		"text": "Camera Serial"
    	},
    	"element": {
    		"type": "plain_text_input",
    		"action_id": "camera_serial",
    		"placeholder": {
    			"type": "plain_text",
    			"text": "Enter a serial number"
    		}
    	}
    }]
}
