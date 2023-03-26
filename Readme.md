# How to use The Configuration service API

## Setup
- Install Docker - https://docs.docker.com/get-docker/
- Install curl - https://everything.curl.dev/get
- To start the services run `docker-compose up` from the main folder

## Using the  configuration service API
- To fetch the configuration run `curl --location --request GET 'http://127.0.0.1:8000'`
- To update the configuration run `curl --location --request POST 'http://127.0.0.1:8000' \
--header 'Content-Type: application/json' \
--data-raw '["str1","str2"]'` - the list can be replaced with the new configuration you want

## Using the anti virus service API
- To scan run `curl --location --request POST 'http://127.0.0.1:8001/scan' \
--form 'file=@"test.txt"'` from the antivirus_service (It scans the test file), the response is a `job_id` that can be used to get the scan status
- To get scan status run `curl --location --request GET 'http://127.0.0.1:8001/scan_status/<job_id>'`, put the job_id from the previous response
