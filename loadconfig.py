import json

with open('config.json') as config_file:
    data = json.load(config_file)

bot_token_prod = data['bot_token_prod']
db_host = data['db_host']
db_name = data['db_name']
db_user = data['db_user']
db_pass = data['db_pass']
precursor_id = data["precursor_id"]
precursor_name = data["precursor_name"]