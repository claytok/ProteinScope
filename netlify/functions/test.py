import json

def handler(event, context):
    """Simple test function to verify Netlify functions are working"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({
            'message': 'Netlify function is working!',
            'method': event['httpMethod'],
            'path': event['path']
        })
    } 