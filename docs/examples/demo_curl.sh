
# Read command-line arguments
if [ $# -eq 0 ]; then
    echo "Usage: curl.sh FILENAME.json"
    exit 1
fi
FileName="$1"

# Send an API request to POST /orders with a JSON request body
API_URL='https://89c3l4f2cd.execute-api.us-east-1.amazonaws.com/prod'
set -x
curl -i -X POST $API_URL/orders -H 'Content-Type: application/json' -d @$FileName
