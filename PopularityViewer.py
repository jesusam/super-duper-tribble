import requests
import json




# HACK: Need to obfuscate this
user_token = "53d9f210be070133cea10b62e6ac3a89"
token_field = "token=" + user_token

groups_endpoint = "https://api.groupme.com/v3/groups"

# Fetch user groups
groups = []

curr_page = 1
per_page = 15
while True:
  curr_page_field = "page=" + str(curr_page)
  per_page_field = "per_page=" + str(per_page)
  groups_url = groups_endpoint + "?" + token_field + "&" + curr_page_field + "&" + per_page_field

  groups_response = requests.get(groups_url)
  groups_data = json.loads(groups_response.content)
  groups_data_response = groups_data['response']

  groups.extend(groups_data_response)

  curr_page = curr_page + 1

  if len(groups_data['response']) < per_page:
    break

print "Showing " + str(len(groups)) + " groups"
print "----------------------------------"
for group in groups:
  print group['name']




# TODO: Have user select a group
selected_group = groups[0]

# Fetch group members
group_members = selected_group['members']
group_members_dict = {}

print "\n\n"
print "Showing " + str(len(group_members)) + " group members in " + selected_group['name']
print "----------------------------------"
for member in group_members:
  print member['nickname']
  group_members_dict[member['user_id']] = member['nickname']




# Build likes map
likes_map = {}
for member_i in group_members:
  user_id_i = member_i['user_id']
  likes_map[user_id_i] = {"all": 0}
  for member_j in group_members:
    user_id_j = member_j['user_id']
    likes_map[user_id_i][user_id_j] = 0

# Count all user likes
message_limit = 100
message_limit_field = "limit=" + str(message_limit)
messages_endpoint = "http://api.groupme.com/v3/groups/" + selected_group['group_id'] + "/messages?" + token_field
messages_url = messages_endpoint + "&" + message_limit_field

messages_response = requests.get(messages_url)
messages_data = json.loads(messages_response.content)
messages_data_response = messages_data['response']
last_message_id = "0"

while True:
  messages = messages_data_response['messages']
  
  for message in messages:
    last_message_id = message['id']
    message_user_id = message['user_id']

    if not message_user_id in likes_map:
      continue
  
    for favorite in message['favorited_by']:
      if not favorite in likes_map:
        continue

      likes_map[message_user_id]['all'] = likes_map[message_user_id]['all'] + 1
      likes_map[message_user_id][favorite] = likes_map[message_user_id][favorite] + 1
      
  messages_url = messages_endpoint + "&" + message_limit_field + "&before_id=" + last_message_id
  messages_response = requests.get(messages_url)

  if not messages_response.status_code == 200:
    break

  messages_data = json.loads(messages_response.content)
  messages_data_response = messages_data['response']

print "\n\n"
for member in group_members:
  member_id = member['user_id']
  member_likes = likes_map[member_id]
  print member['nickname'] + ": " + str(member_likes['all'])

  for key, val in member_likes.iteritems():
    if key == "all":
      continue
    print "\t" + group_members_dict[key] + ": " + str(val)

  print "\n"

## TODO: Remove this. Only here for debugging reasons
#print "\n\n"
#print "likes map: " + str(likes_map)
