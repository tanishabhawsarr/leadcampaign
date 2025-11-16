# from azure.data.tables import TableServiceClient
# from datetime import datetime
# import json
# import os
# from dotenv import load_dotenv

# load_dotenv()

# connection_string =  os.getenv("AZURE_CONNECTION_STRING")
# table_name = os.getenv("TABLE_NAME")

# service = TableServiceClient.from_connection_string(conn_str=connection_string)
# table_client = service.get_table_client(table_name=table_name)


# # 🎯 Function to fetch ONLY the latest lead for a specific email
# def fetch_new_leads(target_email):
#     entities = table_client.list_entities()

#     # Sort newest first
#     entities_sorted = sorted(
#         entities,
#         key=lambda e: datetime.strptime(
#             e.get("CreatedTime", "01/01/2000 00:00:00"), "%m/%d/%Y %H:%M:%S"
#         ),
#         reverse=True,
#     )

#     for entity in entities_sorted:
#         try:
#             customer_info = json.loads(entity.get("CustomerInfo", "{}"))
#             email = customer_info.get("Email", "")
#             if email.lower() == target_email.lower():
#                 return {
#                     "CreatedTime": entity.get("CreatedTime", ""),
#                     "Name": f"{customer_info.get('FirstName', '')} {customer_info.get('LastName', '')}",
#                     "Email": email,
#                     "Company": customer_info.get("Company", ""),
#                     "LeadSource": entity.get("LeadSource", ""),
#                     "ActionCode": entity.get("ActionCode", ""),
#                     "PublisherDisplayName": entity.get("PublisherDisplayName", ""),
#                     "OfferDisplayName": entity.get("OfferDisplayName", ""),
#                     "Description": entity.get("Description", "")
#                 }
#         except Exception:
#             continue

#     return None



# fetchdata.py
# fetchdata.py

# from azure.data.tables import TableServiceClient
# from datetime import datetime, date
# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()

# CONN_STR = os.getenv("AZURE_CONNECTION_STRING")
# TABLE_NAME = os.getenv("TABLE_NAME")

# service = TableServiceClient.from_connection_string(CONN_STR)
# table_client = service.get_table_client(table_name=TABLE_NAME)

# CREATED_FORMAT = "%m/%d/%Y %H:%M:%S"


# # fetchdata.py

# # def fetch_new_leads_since(cutoff_timestamp):
# #     today = date.today()
# #     results = []

# #     entities = table_client.list_entities()

# #     for entity in entities:
# #         created_str = entity.get("CreatedTime", "")
# #         created_dt = datetime.strptime(created_str, "%m/%d/%Y %H:%M:%S")

# #         if created_dt.date() != today:
# #             continue

# #         # Only get leads newer than cutoff time
# #         if cutoff_timestamp and created_dt <= cutoff_timestamp:
# #             continue

# #         customer = json.loads(entity.get("CustomerInfo", "{}") or "{}")

# #         results.append({
# #             "PartitionKey": entity["PartitionKey"],
# #             "RowKey": entity["RowKey"],
# #             "CreatedTime": created_str,
# #             "Created_dt": created_dt,
# #             "Name": f"{customer.get('FirstName', '')} {customer.get('LastName', '')}",
# #             "Email": customer.get("Email", ""),
# #             "Company": customer.get("Company", ""),
# #             "OfferDisplayName": entity.get("OfferDisplayName", ""),
# #             "LeadSource": entity.get("LeadSource", "")
# #         })

# #     results.sort(key=lambda x: x["Created_dt"], reverse=True)
# #     return results


# def fetch_new_leads_since(cutoff_timestamp):
#     results = []

#     entities = table_client.list_entities()

#     for entity in entities:
#         try:
#             created_str = entity.get("CreatedTime", "")
#             created_dt = datetime.strptime(created_str, "%m/%d/%Y %H:%M:%S")

#             # Only show leads created AFTER last processed time
#             if cutoff_timestamp and created_dt <= cutoff_timestamp:
#                 continue

#             customer = json.loads(entity.get("CustomerInfo", "{}") or "{}")

#             results.append({
#                 "PartitionKey": entity["PartitionKey"],
#                 "RowKey": entity["RowKey"],
#                 "CreatedTime": created_str,
#                 "Created_dt": created_dt,
#                 "Name": f"{customer.get('FirstName', '')} {customer.get('LastName', '')}",
#                 "Email": customer.get("Email", ""),
#                 "Company": customer.get("Company", ""),
#                 "OfferDisplayName": entity.get("OfferDisplayName", ""),
#                 "LeadSource": entity.get("LeadSource", "")
#             })

#         except Exception:
#             continue

#     results.sort(key=lambda x: x["Created_dt"], reverse=True)
#     return results



from azure.data.tables import TableServiceClient
from datetime import datetime, date
import os
import json
from dotenv import load_dotenv

load_dotenv()

CONN_STR = os.getenv("AZURE_CONNECTION_STRING")
TABLE_NAME = os.getenv("TABLE_NAME")

service = TableServiceClient.from_connection_string(CONN_STR)
table_client = service.get_table_client(table_name=TABLE_NAME)


# ---------------------------
# SMART DATETIME PARSER
# ---------------------------
def parse_datetime(dt_str):
    dt_str = dt_str.strip()

    formats = [
        "%m/%d/%Y %H:%M:%S",        # 11/15/2025 20:02:52
        "%m/%d/%Y, %I:%M:%S %p",    # 11/15/2025, 8:02:52 PM
        "%d/%m/%Y %H:%M:%S",        # 15/11/2025 20:02:52
        "%d/%m/%Y, %I:%M:%S %p",    # 15/11/2025, 8:02:52 PM
        "%Y-%m-%d %H:%M:%S",        # 2025-11-15 20:02:52
        "%d-%m-%Y %H:%M:%S",        # 15-11-2025 20:02:52
        "%Y/%m/%d %H:%M:%S",        # 2025/11/15 20:02:52
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except:
            pass

    return None   # Unparsable


# ---------------------------
# FETCH NEW LEADS SINCE CUT-OFF
# ---------------------------
def fetch_new_leads_since(cutoff_timestamp):
    results = []
    today = date.today()

    entities = table_client.list_entities()

    for entity in entities:

        created_str = entity.get("CreatedTime", "").strip()
        created_dt = parse_datetime(created_str)

        # If date cannot be parsed → skip lead
        if not created_dt:
            continue

        # Only show today's leads
        if created_dt.date() != today:
            continue

        # Only fetch leads AFTER last processed
        if cutoff_timestamp and created_dt <= cutoff_timestamp:
            continue

        # Parse customer info
        customer = json.loads(entity.get("CustomerInfo", "{}") or "{}")

        results.append({
            "PartitionKey": entity["PartitionKey"],
            "RowKey": entity["RowKey"],
            "CreatedTime": created_str,
            "Created_dt": created_dt,
            "Name": f"{customer.get('FirstName', '')} {customer.get('LastName', '')}",
            "Email": customer.get("Email", ""),
            "Company": customer.get("Company", ""),
            "OfferDisplayName": entity.get("OfferDisplayName", ""),
            "LeadSource": entity.get("LeadSource", "")
        })

    # Sort newest first
    results.sort(key=lambda x: x["Created_dt"], reverse=True)

    return results
