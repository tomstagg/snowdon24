import json

# results = open('scraped_results.json').load()
# print(results)


with open("scraped_results.json", "r") as f:
    results = json.load(f)


def unnest(data):
    unnested = []
    for item in data:
        for lap_details in item["lap_details"]:
            new_item = {
                "place": int(item["place"].rstrip(".")),
                "bib": item["bib"],
                "class": item["class"],
                "name": item["name"],
                "gender": item["gender"],
                "ag": item["ag"],
                "club": item["club"],
                "time": item["time"],
                "gap": item["gap"],
                "laps": item["laps"],
                "award": item["award"],
                "lap": lap_details["lap"],
                "lap_time": lap_details["lap_time"],
                "lap_time_secs": time_to_secs(lap_details["lap_time"]),
                "total": lap_details["total"],
                "total_secs": time_to_secs(lap_details["total"]),
            }
            unnested.append(new_item)
    return unnested


def time_to_secs(time_str):
    h, m, s = time_str.split(":")
    h, m, s = int(h), int(m), int(s)
    total_secs = h * 3600 + m * 60 + s
    return total_secs


unnest_results = unnest(results)
for item in unnest_results[:5]:
    print(item)


with open("cleaned_results.json", "w") as f:
    json.dump(unnest_results, f)
