def combine_results(results):
    #Combine and deduplicate results from multiple tools.

    print(f"Raw Combined Input: {results}")  # Debug input to the function

    combined = {
        "subdomains": set(),
        "ips": set(),
        "emails": set(),
        "hosts": set(),  # Add hosts
        "geo_asn_info": [],  # Add geo_asn_info
    }

    for result in results:
        if isinstance(result, dict):
            combined["subdomains"].update(result.get("subdomains", []))
            combined["ips"].update(result.get("ips", []))
            combined["emails"].update(result.get("emails", []))
            combined["hosts"].update(result.get("hosts", []))

            for info in result.get("geo_asn_info", []):
                if info not in combined["geo_asn_info"]:
                    combined["geo_asn_info"].append(info)

    final_combined = {
        "subdomains": list(combined["subdomains"]),
        "ips": list(combined["ips"]),
        "emails": list(combined["emails"]),
        "hosts": list(combined["hosts"]),
        "geo_asn_info": combined["geo_asn_info"],
    }
    print(f"Final Combined Results: {final_combined}")  # Debug output of the function
    return final_combined
