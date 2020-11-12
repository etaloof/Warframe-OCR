import requests
import time
from db_operations import write_relic, write_part

wf_data_url = 'https://drops.warframestat.us/data/relics.json'
market_api_url = 'https://api.warframe.market/v1/'

data_drop = requests.get(url=wf_data_url).json()

# elements a insérer :
# Table relique - > r_era, r_name, r_reward_1, r_reward_2, r_reward_3, r_reward_4, r_reward_5, r_reward_6_q
# Table items -> item_url, item_name, price_plat, price_ducats
# Procédure -> Insérer la relique et ses 5 rewards, puis ensuite insérer les items correspondant en table avant de passer a la relique suivante
# 25.33, 11.00, 2.00


def check_name(name):
    
    check_list = ['Systems', 'Chassis', 'Neuroptics', 'Receiver', 'Stock', 'Barrel', 'Link', 'Carapace', 'Cerebrum',
                  'Harness', 'Blade', 'Pouch', 'Disc', 'Grip', 'String', 'Handle', 'Ornament', 'Wings', 'Blades', 'Hilt']
                  
    # Special check for extra 'blueprints'
    if any(ele in name for ele in check_list):
        if ' Blueprint' in name:
            item_name = name.replace(' Blueprint', '')
        else:
            item_name = name
    # Special check for Kavasa and Kubrow
    #elif "Kavasa" in name:
    #    if "Kubrow" in name:
    #        item_name = name.replace('Kubrow ', '')
    #    else:
    #        item_name = name.replace('Prime', 'Prime Collar')
    else:
        item_name = name
        
    return item_name


def process_item(item_name):

    check_list = ['Forma', 'Kuva', 'Ayatan', 'Riven', 'Exilus', 'Lohk', 'Xata', 'Jahu', 'Vome', 'Ris', 'Fass', 'Netra', 'Khra']
    
    # Special check for formas
    if any(ele in item_name for ele in check_list):
        return 0, 0
    else:
        if "&" in item_name:
            item_name = item_name.replace('&', 'and')
        else:
            pass
        
        market_item_url = market_api_url + 'items/' + item_name.replace(' ', '_').lower()
        market_stats_url = market_api_url + 'items/' + item_name.replace(' ', '_').lower() + '/statistics'
        
        print(market_stats_url)
        
        data_stats = requests.get(url=market_stats_url).json()
        data_item = requests.get(url=market_item_url).json()
        
        price_plat = data_stats['payload']['statistics_closed']['90days'][-1]['avg_price']
        price_ducats = 0
        
        for element in data_item['payload']['item']['items_in_set']:
            if element['url_name'] == item_name.replace(' ', '_').lower():
                price_ducats = element['ducats']
            else:
                pass
        
        return price_plat, price_ducats


for relic in data_drop['relics']:
    if relic['state'] == 'Intact':
        r_era = relic['tier']
        r_name = relic['relicName']
        item_dict = {}
        uncm_count = 1
        cmn_count = 1
        for item in relic['rewards']:
            time.sleep(0.5)
            itemName = check_name(item['itemName'])
            if item['chance'] == 11:
                item_dict['uncommon_' + str(uncm_count)] = itemName
                uncm_count += 1
            elif item['chance'] == 2:
                item_dict['rare'] = itemName
            else:
                item_dict['common_' + str(cmn_count)] = itemName
                cmn_count += 1
            
            price_plat, price_ducats = process_item(itemName)
            write_part(itemName, price_plat, price_ducats)
            
        write_relic(r_era, r_name, item_dict['common_1'], item_dict['common_2'], item_dict['common_3'], item_dict['uncommon_1'], item_dict['uncommon_2'], item_dict['rare'])
        
    else:       
        pass
