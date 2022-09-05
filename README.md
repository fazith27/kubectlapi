# kubectlapi
REST api for running kubectl commands from Slack bot slash commands. It can be integrated to slack bot to simplify the process of running kubectl cli commands from slack using slash commands. This should be run as a deployment on the EKS cluster in which we would like to run the kubectl command

## Container Environment variables
Below env variables are required and needs to passed when starting the pod (deployment).

Environment Variables | Description
--- | --- 
CLUSTER_NAME | Name of the cluster to run kubectl command against
ROLE_NAME | Role name use to run the kubectl. Role should have access to run kubectl. 
TOKEN | Slack bot token to validate the request are from slack 
CHANNEL | Channel name from which to execute the slash command 
COMMAND | Name of slack slash command

## API Specification
### API Name: Health Check API
Description | Value
--- | ---
Request Resource | /
Request Method | GET
Request Params / Body | NA
Success Response Code | 200
Success Response Message |  "I am OK !"
Error Response | NA

### API Name: Kubectl Python App
Description | Value
--- | ---
Request Resource | /kubectl
Request Method | POST
Kubectl Operations Supported | kubectl get, describe and version
Request Params/Body | token,channel_name,command,text,response_url
Success Response Code | 200
Success Response Message | {"body":"null","headers":{"Content-Type":"application/json"},"statusCode":200}
Slack Message Response | {'text': <kubectl response>,'channel': <authored channel>}
Error Response Code (when any of the required request param missing) | 200
Slack Response  Message | {"body":"{\"response_type\": \"in_channel\", \"text\": \"Bad Request\"}","headers":{"Content-Type":"application/json"},"statusCode":200}
Error Response Code (during runtime error) |  200
Slack Response  Message | {"body":"{\"response_type\": \"in_channel\", \"text\": \"Runtime Error\"}","headers":{"Content-Type":"application/json"},"statusCode":200}
  
> Slack expect a immediate response (with in 3 seconds) to confirm the payload is received, hence sending response code as 200 for all the scenarios even though when there is an error. Actual kubectl response will send back to slack using the *response_url* (slack webhook) receveid in request in a seperate thread.

## Request Flow
![Request Flow Image](https://github.com/fazith27/kubectlapi/blob/main/request-flow.png)

## Slash command input validation
* Kubectl queries which are starting with below values will be processed. Rest of the values are responded with Invalid Request response.
> Allowed values = ['kubectl get', 'kubectl version','kubectl describe']

* Kubectl queries which have any of the below values will be blocked and will not be processed.
> Blocked values = ['>','<','&','kubectl get log']

* Request params token, channel_name and command will be validated against the environment variable of the container.
