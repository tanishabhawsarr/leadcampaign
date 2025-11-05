from azure.data.tables import TableServiceClient
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()
connection_string =  os.getenv("AZURE_TABLE_CONNECTION_STRING")
table_name = os.getenv("TABLE_NAME")

service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = service.get_table_client(table_name=table_name)


# 🎯 Function to fetch ONLY the latest lead for a specific email
def fetch_new_leads(target_email):
    entities = table_client.list_entities()

    # Sort newest first
    entities_sorted = sorted(
        entities,
        key=lambda e: datetime.strptime(
            e.get("CreatedTime", "01/01/2000 00:00:00"), "%m/%d/%Y %H:%M:%S"
        ),
        reverse=True,
    )

    for entity in entities_sorted:
        try:
            customer_info = json.loads(entity.get("CustomerInfo", "{}"))
            email = customer_info.get("Email", "")
            if email.lower() == target_email.lower():
                return {
                    "CreatedTime": entity.get("CreatedTime", ""),
                    "Name": f"{customer_info.get('FirstName', '')} {customer_info.get('LastName', '')}",
                    "Email": email,
                    "Company": customer_info.get("Company", ""),
                    "LeadSource": entity.get("LeadSource", ""),
                    "ActionCode": entity.get("ActionCode", ""),
                    "PublisherDisplayName": entity.get("PublisherDisplayName", ""),
                    "OfferDisplayName": entity.get("OfferDisplayName", ""),
                    "Description": entity.get("Description", "")
                }
        except Exception:
            continue

    return None


