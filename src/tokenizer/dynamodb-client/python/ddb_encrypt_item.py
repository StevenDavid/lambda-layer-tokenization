import boto3

from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions

def encrypt_item (plaintext_item,table_name):
    #table_name='CreditCardTokenizerTable'
    table = boto3.resource('dynamodb').Table(table_name)

    aws_cmk_id='arn:aws:kms:us-west-2:176385768664:key/bd3a8796-1638-42f3-b318-ac357427f326'
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)

    actions = AttributeActions(
        default_action=CryptoAction.ENCRYPT_AND_SIGN,
        attribute_actions={'Account_Id': CryptoAction.DO_NOTHING}
    )

    encrypted_table = EncryptedTable(
        table=table,
        materials_provider=aws_kms_cmp,
        attribute_actions=actions
    )
    
    print (plaintext_item)
    response = encrypted_table.put_item(Item=plaintext_item)

    print(response)
    return response 

def get_decrypted_item (index_key,table_name):
    #table_name='CreditCardTokenizerTable'
    table = boto3.resource('dynamodb').Table(table_name)

    aws_cmk_id='arn:aws:kms:us-west-2:176385768664:key/bd3a8796-1638-42f3-b318-ac357427f326'
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)

    actions = AttributeActions(
        default_action=CryptoAction.ENCRYPT_AND_SIGN,
        attribute_actions={'Account_Id': CryptoAction.DO_NOTHING}
    )

    encrypted_table = EncryptedTable(
        table=table,
        materials_provider=aws_kms_cmp,
        attribute_actions=actions
    )


    response = encrypted_table.get_item(Key=index_key)
    
    return response


def get_item (index_key,table_name):
    #table_name='CreditCardTokenizerTable'
    table = boto3.resource('dynamodb').Table(table_name)

    response = table.get_item(Key=index_key)

    return response 
