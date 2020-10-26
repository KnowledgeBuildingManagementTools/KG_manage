import requests

from KG_manage import settings

headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}
data = requests.post(settings.neo4j_ip + '/kg/graph/query',
                     data={"start_node_uuid ": '7d781b8d-4c03-531c-a762-0ff4c2bbe535', "relation_type": ["专业领域"], "headers":headers})
data = data.json()