import pandas as pd

def export_to_excel(data, file_path):
    """
    Export scan data to an Excel file.
    """
    results = []
    for subdomain in data["results"].get("subdomains", []):
        results.append({"Type": "Subdomain", "Value": subdomain})

    for host in data["results"].get("hosts", []):
        results.append({"Type": "Host", "Value": host})

    for ip in data["results"].get("ips", []):
        results.append({"Type": "IP Address", "Value": ip})

    for email in data["results"].get("emails", []):
        results.append({"Type": "Email", "Value": email})

    for geo in data["results"].get("geo_asn_info", []):
        results.append({
            "Type": "Geolocation",
            "Value": f"IP: {geo['ip']}, City: {geo['city']}, Country: {geo['country']}, ASN: {geo['asn']}, Org: {geo['org']}"
        })

    if not results:
        print("No data to export!")

    # Convert to DataFrame and save
    df = pd.DataFrame(results)
    df.to_excel(file_path, index=False)

