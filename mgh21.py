import os
import subprocess
import secrets
from eth_account import Account
import json

# Step 2: Create directories for node1, node2, and node3
os.makedirs("node1", exist_ok=True)
os.makedirs("node2", exist_ok=True)
os.makedirs("node3", exist_ok=True)

# Step 3: Generate private keys and addresses for node1, node2, and node3
priv_key_1 = secrets.token_hex(32)
priv_key_2 = secrets.token_hex(32)
priv_key_3 = secrets.token_hex(32)

address_1 = Account.from_key(priv_key_1).address
address_2 = Account.from_key(priv_key_2).address
address_3 = Account.from_key(priv_key_3).address

# Step 4: Generate custom extraData
vanity = "0" * 64  # 32 bytes
sig = "0" * 130  # 65 bytes

extraData = "0x" + vanity + address_1[2:] + address_2[2:] + address_3[2:] + sig

# Step 5: Modify the genesis.go file
genesis_file_path = "/home/ubuntu/qng/meerevm/amana/genesis.go"  # Update the path to the correct location
with open(genesis_file_path, "r") as genesis_file:
    genesis_content = genesis_file.read()

genesis_content = genesis_content.replace(
    "hexutil.MustDecode(\"0x00000000000000000000000000000000000000000000000000000000000000007>",
    f"hexutil.MustDecode(\"{extraData}\")"
)

with open(genesis_file_path, "w") as genesis_file:
    genesis_file.write(genesis_content)

# Step 6: Create the config.toml files for each node
# Define the content for the config.toml file
config_content = """
privnet=true
amana=true
norpc=true
"""

# Define the list of node directories, their corresponding addresses, and ports
node_directories = ["node1", "node2", "node3"]
node_addresses = [address_1, address_2, address_3]
node_ports = [37000, 38000, 39000]
http_ports = [8575, 8580, 8585]

# Create the config.toml file in each node directory
for node_directory, node_address, node_port, http_port in zip(node_directories, node_addresses, node_ports, http_ports):
    config_path = os.path.join(node_directory, 'config.toml')

    with open(config_path, 'w') as config_file:
        config_file.write(f"{config_content}\namanaenv=\"--unlock {node_address} --port {node_port} --http.port {http_port} --password password.txt --http --http.api=eth,net,web3,amana --http.corsdomain=* --http.port {http_port} --allow-insecure-unlock miner.etherbase {node_address} --mine\"")

print("Config.toml files have been created in the node directories.")

# Run cleanup to generate the necessary files for each node
NODE_1_DIRECTORY = "/home/ubuntu/node1"  # Update the path to the correct location
NODE_2_DIRECTORY = "/home/ubuntu/node2"  # Update the path to the correct location
NODE_3_DIRECTORY = "/home/ubuntu/node3"  # Update the path to the correct location

PRIV_KEY_1 = priv_key_1  # Replace with the actual private key for node 1
PRIV_KEY_2 = priv_key_2  # Replace with the actual private key for node 2
PRIV_KEY_3 = priv_key_3  # Replace with the actual private key for node 3

# Change directory and run qng for each node
for node_directory, node_port in zip([NODE_1_DIRECTORY, NODE_2_DIRECTORY, NODE_3_DIRECTORY], node_ports):
    os.chdir(node_directory)
    subprocess.run(["sudo", "./qng", "-A", "./", "--privnet", "--amana", f"--port {node_port}", "--cleanup"])

# Define a function to generate keystore files
def keystore():
    print("Generating keystore files for each node...")

    # Create keystore directories
    for node_directory, priv_key_index in zip([NODE_1_DIRECTORY, NODE_2_DIRECTORY, NODE_3_DIRECTORY], range(1, 4)):
        keystore_dir = os.path.join(node_directory, "data/privnet/keystore")
        os.makedirs(keystore_dir, exist_ok=True)

        # Encrypt private key using the passphrase "amana1"
        encrypted_key = Account.encrypt(eval(f"PRIV_KEY_{priv_key_index}"), "amana1")

        keystore_file_path = os.path.join(keystore_dir, f"keystore_{priv_key_index}.json")

        with open(keystore_file_path, "w") as keystore_file:
            keystore_json = json.dumps(encrypted_key, indent=4)
            keystore_file.write(keystore_json)

        # Copy password.txt to unlock accounts
        subprocess.run(["cp", "password.txt", node_directory])

# Call the keystore function
keystore()
