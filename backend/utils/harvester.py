import asyncio
import platform
import socket
import os
import yaml
import json
import aiohttp
from theHarvester.theHarvester.discovery.bingsearch import SearchBing

# Ensure SelectorEventLoop is used on Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch_geolocation_and_asn(ip, api_keys):
    """
    Fetch geolocation and ASN information for an IP address using Shodan or other APIs.
    """
    shodan_api_key = api_keys.get('shodan', {}).get('api_key')
    if not shodan_api_key:
        print("Shodan API key not found. Skipping geolocation and ASN lookup.")
        return None

    url = f"https://api.shodan.io/shodan/host/{ip}?key={shodan_api_key}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "ip": ip,
                        "city": data.get("city"),
                        "country": data.get("country_name"),
                        "asn": data.get("asn"),
                        "org": data.get("org")
                    }
                else:
                    print(f"Failed to fetch geolocation for {ip}. Status code: {response.status}")
        except Exception as e:
            print(f"Error fetching geolocation for {ip}: {e}")

    return None

async def harvest_info(domain, sources=['bing'], limit=100):
    """
    Perform OSINT gathering using theHarvester and additional APIs.

    Args:
        domain (str): Target domain to search.
        sources (list): List of search engines to use.
        limit (int): Maximum results to fetch.

    Returns:
        dict: Dictionary containing gathered information.
    """
    results = {
        'emails': set(),
        'hosts': set(),
        'ips': set(),
        'geo_asn_info': []
    }

    # Load API keys
    with open(os.path.expanduser(r'C:\Users\theka\PycharmProjects\pythonProject\theHarvester\api-keys.yaml'), 'r') as file_path:
        api_keys = yaml.safe_load(file_path)
        print("Loaded API keys:", api_keys)

    for source in sources:
        try:
            if source == 'bing':
                search = SearchBing(domain, limit=limit, start=5)

                # Validate API key
                api_key = api_keys.get('bing', {}).get('api_key')
                if not api_key:
                    raise ValueError("Bing API key is missing or invalid in api-keys.yaml.")
                print(f"Using Bing API key: {api_key}")

                # Process Bing search
                await search.process(api=api_key)

                # Await async methods
                results['emails'].update(await search.get_emails())
                results['hosts'].update(await search.get_hostnames())

                # Resolve IPs
                for host in await search.get_hostnames():
                    try:
                        ip = socket.gethostbyname(host)
                        results['ips'].add(ip)
                    except socket.gaierror:
                        print(f"Error resolving host {host}")
                        continue

        except Exception as e:
            print(f"Error processing {source}: {str(e)}")
            continue

    # Fetch geolocation and ASN info for IPs
    for ip in results['ips']:
        geo_asn_info = await fetch_geolocation_and_asn(ip, api_keys)
        if geo_asn_info:
            results['geo_asn_info'].append(geo_asn_info)

    # Convert sets to lists for export compatibility
    return {
        'emails': list(results['emails']),
        'hosts': list(results['hosts']),  # Ensure hosts are included
        'ips': list(results['ips']),
        'geo_asn_info': results['geo_asn_info']  # Ensure geolocation data is included
    }


async def save_results_to_file(domain, results):
    """
    Save the results to a JSON file for future reference.

    Args:
        domain (str): Target domain.
        results (dict): Gathered information.
    """
    output_file = f"{domain}_osint_results.json"
    try:
        with open(output_file, 'w') as file:
            json.dump(results, file, indent=4)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

# Example usage
async def main():
    target_domain = "google.com"
    results = await harvest_info(target_domain)

    print("\nFound Emails:")
    for email in results['emails']:
        print(f"- {email}")

    print("\nFound Hosts:")
    for host in results['hosts']:
        print(f"- {host}")

    print("\nFound IPs:")
    for ip in results['ips']:
        print(f"- {ip}")

    print("\nGeolocation and ASN Info:")
    for info in results['geo_asn_info']:
        print(f"- {info}")

    # Save results to file
    await save_results_to_file(target_domain, results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())