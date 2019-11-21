# AppsFlyer-GDPR-Deletion-Script
A script that takes a CSV list of devices and will send the deletion requests to AppsFlyer and store the request ID should you need to check on the deletion status

This custom script is NOT intended as a solution to offer clients. This is something exclusively for one-off requests or GDPR testing.  

### Requirements of using this script:
1. Python 3

Python libraries needed:
* requests
* json
* pandas
* tqdm
* datetime
* uuid
* warnings
* math
* time

You will also need a CSV file with 3 columns:
* app_id (exactly as it appears in AppsFlyer UI
* Platform (only supports iOS and Android currently)
* Device ID (only supports IDFA or Advertising ID currently)


### How to use this script:
1. Download the attached script and put it on your desktop or in a folder on your desktop
1. Generate or find your CSV file and make sure to place this wherever you placed the python script from above (they need to be in the same location / folder)
I've provided a sample file for reference and so you can test this:
1. Open Terminal (this is the part that might scare some of y'all but just tap a support engineer on the should and we can help with this section)
1. Navigate (in terminal to where you have stored the CSV and script)
1. Run "python GDPR_delete.py":
1. The script will ask you for your AppsFlyer API Key, if this is a test and file name
Provide your API key 
  1. If this is a test, the script will use the StubAPI endpoint (for testing only).
  1. If is_test marked as true, you can also request to see raw logs (it will ask for debug logs enabled)
  1. Provide your file name (for example: "test.csv")
1. Sit back and relax. The script will do all the rest!

_At the end, the script will create a new CSV with _LOG added to the end (so test.csv becomes test_LOG.csv)
Review this file to confirm all uploads were successful. Refer to the "error_status" column for any issues _
