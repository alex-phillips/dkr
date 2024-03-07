import json, subprocess, re

result = subprocess.run(f"docker ps -aq | xargs docker inspect", capture_output=True, shell=True, text=True)
containers = json.loads(result.stdout)
# print(containers)

nas_containers = []
for container in containers:
    for mount in container["Mounts"]:
        if re.search(r"\/mnt\/storage", mount["Source"]):
            # nas_containers.append(container["Id"])
            nas_containers.append(container["Name"].replace("/", ""))
            break

print(" ".join(nas_containers))
