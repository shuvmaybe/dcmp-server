import json
import argparse

parser = argparse.ArgumentParser(description="Combine unobf and obf options")
parser.add_argument("dev_json", help="Path to the obfuscated JSON file")
parser.add_argument("prod_json", help="Path to the deobf JSON file")
parser.add_argument("output_json", help="Path for the combined output JSON")
args = parser.parse_args()

# Use:
# deobfuscated.json obfuscated.json output.json

with open(args.dev_json, "r") as f:
    dev_data = json.load(f)

with open(args.prod_json, "r") as f:
    prod_data = json.load(f)

combined_data = {}
dev_keys = list(dev_data.keys())
prod_keys = list(prod_data.keys())

if len(dev_keys) != len(prod_keys):
    print("warning!!: dev and prod jsons have different number of options")

for i, dev_key in enumerate(dev_keys):
    try:
        prod_key = prod_keys[i]
    except IndexError:
        print(f"prod json missing field for dev key {dev_key}")
        continue

    dev_entry = dev_data[dev_key]
    if "kind" not in dev_entry:
        print(f"skipping {dev_key}: missing 'kind'")
        continue

    combined_data[dev_key] = {
        "values": dev_entry.get("values"),
        "kind": dev_entry["kind"],
        "field": prod_key
    }


with open(args.output_json, "w") as f:
    json.dump(combined_data, f, indent=4)

print(f"combined json written to {args.output_json}")
