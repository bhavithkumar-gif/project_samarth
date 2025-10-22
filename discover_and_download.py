# discover_and_download.py
import requests, os, time, sys
CKAN_API = "https://www.data.gov.in/api/3/action/package_search"

def search_and_download(query, target_dir="data"):
    params = {"q": query, "rows": 5}
    r = requests.get(CKAN_API, params=params, timeout=30)
    r.raise_for_status()
    results = r.json().get('result', {}).get('results', [])
    if not results:
        print("No packages found for:", query)
        return []
    saved = []
    os.makedirs(target_dir, exist_ok=True)
    for pkg in results:
        print("Package:", pkg.get('title'))
        for res in pkg.get('resources', []):
            url = res.get('url') or res.get('webstore_url')
            if not url: 
                continue
            ext = os.path.splitext(url.split('?')[0])[1].lower()
            if ext in ('.csv','.xlsx','.xls','.parquet'):
                fname = os.path.join(target_dir, res.get('name','resource').replace(' ','_') + ext)
                try:
                    print("Downloading", url)
                    with requests.get(url, stream=True, timeout=60) as rr:
                        rr.raise_for_status()
                        with open(fname, 'wb') as f:
                            for chunk in rr.iter_content(8192):
                                f.write(chunk)
                    print("Saved", fname)
                    saved.append({"pkg":pkg.get('title'), "resource_name":res.get('name'), "file":fname, "url":url})
                    time.sleep(1)
                except Exception as e:
                    print("Failed to download", url, "err:", e)
    return saved

if __name__ == "__main__":
    # crop dataset
    print("=== Searching crop production datasets ===")
    crop_hits = search_and_download("district-wise season-wise crop production")
    print("=== Searching rainfall (IMD) datasets ===")
    rain_hits = search_and_download("rainfall India IMD")
    print("Done. Found:", len(crop_hits), "crop resources and", len(rain_hits), "rain resources.")
    if not (crop_hits and rain_hits):
        print("If downloads failed, use precomputed CSVs in sample_outputs/ for demo.")
