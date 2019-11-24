# Lambda Layer for Tokenization and Encryption of Sensitive Data

This session is designed to familiarize you with how to use [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html). In this session, you will create solve a common problem for generating token for sensitive data within your application and store encrypted data. You will use [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html) to create [customer managed master  key](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#master_keys) which will be used by DynamoDB client encryption library to generate [encryption data keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#data-keys) and this code will be packed into Lambda Layer. This Lambda Layer will be imported into simple ordering application. The application gets the sensitive data from the end user and invokes the imported method to generate unique token to be stored in application database and pass the sensitive data to be stored in encrypted format in another database. When required, this encrypted data will be decrypted by providing the unique token with the required abstraction from the application. 

- src/encryption_keys - This folder contains the cloud formation template to create KMS key
- src/tokenizer  - This folder contains the cloud formation template for creating Lambda Layer and [DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) table, [compile and install required dependencies for Lambda layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) and code for encrypting and decrypting provided strings using [DynamoDB encryption client library](https://docs.aws.amazon.com/dynamodb-encryption-client/latest/devguide/what-is-ddb-encrypt.html).
- src/CustomerApp - This folder contains the cloud formation template to create DynamoDB table, [Lambda Function](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html), [API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html), [Cognito User Pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html) and [Cognito Application Client](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html). It also contains the code for the application when required APIs are invoked through API Gateway. 

## AWS Services Used
 1. [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
 2. [Amazon API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
 3. [Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
 4. [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)
 5. [AWS Cloud9](https://docs.aws.amazon.com/cloud9/latest/user-guide/welcome.html)
 6. [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
 
 
 ## Pre-requisite 
 1. Access to the above mentioned AWS services within AWS Account
 2. This lab assumes that you have logged in as root account into AWS account. If not, then you need to update key policy under template.yaml file under encryption_keys folder. Replace the keyword 'root' with your user in this file.
 3. This lab uses **python**  programming language for Lambda Layer and Lamnda Function application code.
 
 ## Environment Setup
 **Step 1.** This Lab uses AWS Cloud9 as IDE. Complete the Cloud9 Setup in your environment using this [guide](cloud9_setup/README.md)
 
 ## Create S3 Bucket
 **Step 2.**  We need [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/Welcome.html) bucket for [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html). We are going to use AWS SAM in this lab to build and deploy SAM templates (template.yaml). Note that you need to use a unique name for your S3 bucket. Replace unique-s3-bucket-name with the required value.
 
 ```bash
 aws s3 mb s3://<unique-s3-bucket-name>
 ```
 
 ## Initialize and Clone Git into Cloud9 Environment
 
 **Step 3.** Use the below commands to initialize and clone the git repository
 
 ```bash
 git init
 git clone https://github.com/anujag24/lambda-layer-tokenization.git
 ```
 
 Once the git repository is cloned, check the directories on the cloud9 environment. Sample output below-
 
 ![Git Cloned](images/git-cloned.png)
 
 ## Create Customer Managed KMS Key
 
 **Step 4.1** Go to encryption_keys directory

```bash
cd lambda-layer-tokenization/src/encryption_keys
```
 
**Step 4.2** Build the SAM template (template.yaml) under the directory

```bash
sam build --use-container
```
 
**Step 4.3** After the build is successful, below is the output

```diff
 Build Succeeded
```
 
**Step 4.4** Package the SAM template to push the code to S3 Bucket

```bash
sam package --s3-bucket <unique-s3-bucket-name> --output-template-file packaged.yaml
```
 
Expected Output

```diff
Successfully packaged artifacts and wrote output template to file packaged.yaml
```

**Step 4.6** Deploy the stack using below command. Note the name of the stack is **kms-stack**

`sam deploy --template-file ./packaged.yaml --stack-name kms-stack`

*Sample Output* 

```diff
Successfully created/updated stack - kms-stack
```

**Step 4.7** Check the output variables for the stack 

`aws cloudformation describe-stacks --stack-name kms-stack`

*Sample Output*

Note the *OutputValue* of  *OutputKey* **KMSKeyID** from the output

```json
"Outputs": [
                {
                    "Description": "ARN for CMS Key created", 
                    "OutputKey": "KMSKeyID", 
                    "OutputValue": "*********"
                }
            ]
```

In this step, you have created customer managed KMS key and gave permissions to the root user to access the key to perform all operations. This master encryption key will be used to generate data encryption keys for encrypting items later in the lab. 

## Lambda Layer for String Tokenization and Encrypted Data Store
In this section, we will use the customer managed master key created in the earlier stack to create the lambda layer which will be used by application teams to generate token for sensitive data string such as credit card, etc. 

**Step 5.1** Go to tokenizer directory 

```bash
cd /home/ec2-user/lambda-layer-tokenization/src/tokenizer/
```

**Step 5.2** Open the file ddb_encrypt_item.py and update the value of the variable **aws_cmk_id** and save the file

```bash
vi ddb_encrypt_item.py
```

As part of Lambda Layer creation, we need dependent libraries for the application code (ddb_encrypt_item.py) to be installed and provided as part of the lambda layer package. Since the libraries are Operating System (OS) dependent so they have to be compiled on native OS supported by Lambda.

**Step 5.3** Check the dependent libraries mentioned in requirements.txt file

```bash
cat requirements.txt 
```

*Sample Output* 

```bash
dynamodb-encryption-sdk
cryptography
```

**Step 5.4** Run the script to compile and install the dependent libraries in *dynamodb-client/python/* directory. [More Details on this](https://github.com/pyca/cryptography/issues/3051?source=post_page-----f3e228470659----------------------)

```bash
./get_layer_packages.sh
```

**Step 5.5** Copy the python file to *dynamodb-client/python/* which is required for Lambda layer. Lambda layer expects files to be in a specific directory so that it can be used by Lambda function. [More details](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path)

```bash
cp ddb_encrypt_item.py dynamodb-client/python/
```

```bash
cp hash_gen.py dynamodb-client/python/
```

**Step 5.6** Build SAM template 

```bash
sam build --use-container 
```

**Step 5.7** Package the SAM template to push the code to S3 Bucket

```bash
sam package --s3-bucket <unique-s3-bucket-name> --output-template-file packaged.yaml
```
 
*Sample Output*

```diff
Successfully packaged artifacts and wrote output template to file packaged.yaml
```

**Step 5.8** Deploy the stack using below command. Note the name of the stack is **tokenizer-stack**

```bash
sam deploy --template-file ./packaged.yaml --stack-name tokenizer-stack
```

**Step 5.9** Check the output variables for the stack

```bash
aws cloudformation describe-stacks --stack-name tokenizer-stack
```

*Sample Output*

Note the *OutputValue* of *LayerVersionArn* and **DynamoDBArn** from the output

```json
"Outputs": [
                {
                    "Description": "ARN for the published Layer version", 
                    "ExportName": "TokenizeData", 
                    "OutputKey": "LayerVersionArn", 
                    "OutputValue": "***********"
                }, 
                {
                    "Description": "ARN for DynamoDB Table", 
                    "OutputKey": "DynamoDBArn", 
                    "OutputValue": "***********/CreditCardTokenizerTable"
                }

            ]
```

## Serverless Application API for Order Creation and Payment Submission 

**Step 6.1** Go to CustomerApp directory which has Serverless Application
 
 ```bash
 cd /home/ec2-user/lambda-layer-tokenization/src/CustomerApp/
 ```
 
Let’s build the Serveless application which contains API gateway for API management, Lambda Function for application code, Lambda Layer to import reusable code that you created earlier and Cognito for API authentication
 

**Step 6.2** Build SAM template 

```bash
sam build --use-container 
```

**Step 6.3** Package the SAM template to push the code to S3 Bucket

```bash
sam package --s3-bucket <unique-s3-bucket-name> --output-template-file packaged.yaml
```
 
*Sample Output*

```Successfully packaged artifacts and wrote output template to file packaged.yaml```

**Step 6.4** Deploy the stack using below command. Note the name of the stack is **app-stack**. 

Replace the parameters with previously identified values for **LayerVersionArn**, **KMSKeyID** and **DynamoDBArn**

```bash
sam deploy --template-file ./packaged.yaml --stack-name app-stack --capabilities CAPABILITY_IAM --parameter-overrides layerarn=<LayerVersionArn> kmsid=<KMSKeyID> dynamodbarn=<DynamoDBArn>
```

**Step 6.5** Check the output variables for the stack
```bash
aws cloudformation describe-stacks --stack-name app-stack
```

*Sample Output*

Note the *OutputValue* of *OutputKey* **PaymentMethodApiURL** , **AccountId** , **UserPoolAppClientId** and **Region** from the output


```json
"Outputs": [
                {
                    "Description": "Customer Order Lambda Function ARN", 
                    "OutputKey": "CustomerOrderFunction", 
                    "OutputValue": "*******************:app-stack-CustomerOrderFunction*******"
                }, 
                {
                    "Description": "API Gateway endpoint URL for Prod stage for Hello World function", 
                    "OutputKey": "PaymentMethodApiURL", 
                    "OutputValue": "https://*****************/dev/"
                }, 
                {
                    "Description": "AWS Account Id", 
                    "OutputKey": "AccountId", 
                    "OutputValue": "********"
                },
                {
                    "Description": "User Pool App Client for your application", 
                    "OutputKey": "UserPoolAppClientId", 
                    "OutputValue": "********************"
                }, 
                {
                    "Description": "Region", 
                    "OutputKey": "Region", 
                    "OutputValue": "*************"
                }

            ]
```

**Step 6.7** Now, you will create Cognito user for authentication. Open *cognito_commands.sh* file and update the values for YOUR_COGNITO_REGION, YOUR_COGNITO_APP_CLIENT_ID and YOUR_EMAIL as below

```
YOUR_COGNITO_REGION=<Region>

YOUR_COGNITO_APP_CLIENT_ID=<UserPoolAppClientId>

YOUR_EMAIL=<user-email>
```

**Step 6.8** Run the script *cognito_commands.sh*. This script will generate the command required to create new user in Cognito and generate ID token for API authentication.

```bash
./cognito_commands.sh
```

Copy and paste the command generated by the script in the order specified. 

**Step 6.9** Run first Cognito command 

```bash
aws cognito-idp sign-up --region <Region> --client-id <UserPoolAppClientId> --username <user-email> --password <password>
```

*Sample Output* 

```json
{
    "UserConfirmed": false, 
    "UserSub": "************", 
    "CodeDeliveryDetails": {
        "AttributeName": "email", 
        "Destination": "<user-email>", 
        "DeliveryMedium": "EMAIL"
    }
}
```

**Step 6.10** Run second Cognito command  

**Note – You will get email on the specified email Id. Replace CONFIRMATION_CODE_IN_EMAIL with the verification code in the email for below command**

```bash
aws cognito-idp confirm-sign-up --client-id <UserPoolAppClientId>  --username <user-email> --confirmation-code <CONFIRMATION_CODE_IN_EMAIL>
```

*Sample Output*

**Note – There will be no output for this command**

**Step 6.11** Run third Cognito command 

```bash
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id <UserPoolAppClientId> --auth-parameters USERNAME=<user-email>,PASSWORD=<password>
```

*Sample Output*

Note the value of **IdToken** for next steps

```json 
{
    "AuthenticationResult": {
        "ExpiresIn": 3600, 
        "IdToken": "*********", 
        "RefreshToken": "******", 
        "TokenType": "Bearer", 
        "AccessToken": "********"
    }, 
    "ChallengeParameters": {}
}
```

Now, we will invoke APIs to test the application. There are two APIs - 
1. **/order** - The first API i.e. *‘order’* is to create the customer order, generate the token for credit card number (using Lambda Layer) and store encrypted credit card number in another DynamoDB table (as specified in the Lambda Layer) and finally store the customer information along with the credit card token in DynamoDB table namely CustomerOrderTable. 
2. **/paybill** - The second API i.e. *‘paybill’* takes the CustomerOrder number and fetches credit card token from  CustomerOrderTable and calls decrypt method in Lambda Layer to get the deciphered credit card number. 

**Step 6.12** Let's call /order API to create the order as below. Replace the value of **PaymentMethodApiURL** and **IdToken** with the values identified in the previous step. 

```bash
curl -X POST \
 <PaymentMethodApiURL>/order \
-H 'Authorization: <IdToken>' \
-H 'Content-Type: application/json' \
-d '{
"CustomerOrder": "123456789",
"CustomerName": "Amazon Web Services",
"CreditCard": "0000-0000-0000-0000",
"Address": "Reinvent2019, Las Vegas, USA"
}'
```

**Step 6.13** Let's call */paybill* to pay the bill using the previously provided information. Replace the value of **PaymentMethodApiURL** and **IdToken** with the values identified in the previous step. 

```bash
curl -X POST \
 <PaymentMethodApiURL>/paybill \
-H 'Authorization: <IdToken>' \
-H 'Content-Type: application/json' \
-d '{
"CustomerOrder": "123456789"
}'
```

Application has created the order with required details and saved the plain text information in DynamoDB table i.e. **CustomerOrdeTable** and encrypted CreditCard information is stored in another DynamoDB table i.e. **CreditCardTokenizerTable** . Now, check the values in both the tables to see the items stored. 

**Step 6.14** Get the items stored in **CustomerOrdeTable**

```bash
aws dynamodb get-item --table-name CustomerOrderTable --key '{ "CustomerOrder" : { "S": "123456789" }  }'
```

*Sample Output*

Note the value of **CreditCard** from the below output.

```json
{
    "Item": {
        "CustomerOrder": {
            "S": "123456789"
        }, 
        "Address": {
            "S": "Reinvent2019, Las Vegas, USA"
        }, 
        "CustomerName": {
            "S": "Amazon Web Services"
        }, 
        "CreditCard": {
            "S": "**********"
        }
    }
}
```

**Step 6.15** Get the items stored in **CreditCardTokenizerTable**. Replace the value of **CreditCard** and **AccountId** with previously identified values.

```bash
aws dynamodb get-item --table-name CreditCardTokenizerTable --key '{ "Hash_Key" : { "S": "<CreditCard>" }, "Account_Id" : { "S" : "<AccountId>" }  }'
```

*Sample Output*

```json
{
    "Item": {
        "*amzn-ddb-map-sig*": {
            "B": "**************"
        }, 
        "*amzn-ddb-map-desc*": {
            "B": "**************"
        }, 
        "Hash_Key": {
            "S": "***************"
        }, 
        "Account_Id": {
            "S": "***************"
        }, 
        "CandidateString": {
            "B": "*****************"
        }
    }
}
```

## Clean up and Delete the resources

**Step 7.** Delete the three cloud formation stacks created and S3 bucket. Replace the value of **unique-s3-bucket-name** with the name of the bucket created earlier in the lab

```bash
aws cloudformation delete-stack --stack-name app-stack

aws cloudformation delete-stack --stack-name tokenizer-stack

aws cloudformation delete-stack --stack-name kms-stack

aws s3 rb s3://<unique-s3-bucket-name> --force
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
