Podman Pod with Multi-Container
===============================

This repository aims to demonstrate a multi-container application with podman for educational reasons.

Check the files step1.txt, step2.txt, step3.txt, etc to step through this one stage at a time.

## TL;DR of your ports

* Host 8088 --> Pod 8080 --> nginx
* nginx 8080 --> proxy to notes-api 8000 (in-pod)
* notes-api 8000 --> talks to Postgres 5432 (in-pod)
* 5432/8000 are not published to host (only reachable inside the pod)

# Overall description

## How your pod’s networking works

### Pod publish (host <--> pod):
When you created the pod with -p 8088:8080, you told Podman:
### Host TCP 8088 --> Pod’s shared network namespace TCP 8080
Only that mapping is exposed to the host. Nothing else is published.

### Shared net namespace (inside the pod):
All containers in the pod share the same IP and loopback. So:

* Postgres listens on 127.0.0.1:5432 (in-pod)

* notes-api listens on 0.0.0.0:8000 (in-pod)

* nginx listens on 0.0.0.0:8080 (in-pod) and proxies → 127.0.0.1:8000

* From any container in the pod, 127.0.0.1:<port> reaches any other container’s port.

### From the host:

* curl http://127.0.0.1:8088/... --> hits the pod’s 8080 (i.e., nginx), which then proxies to the API.

* DB is not exposed to the host (good security). To reach it from the host you’d need to publish it (e.g., -p 15432:5432 on the pod, not the container), or exec into a pod container.
