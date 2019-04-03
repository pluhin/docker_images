# Jenkins deployment for k8s cluster
## What inside
- [Dockerfile for Jenkis image](./Dockerfile) - wil be as source for Jenkins deployment in the cluster

## K8s deployment
For k8s deployment you can use kubespray, or, for testing - minikube.
How to install minikube:
### Install minikube

Install kubectl

```bash
apt-get -qq update && apt-get install -qqy apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubectl.list
apt-get update -qq
apt-get install -qqy kubectl
```

Install minikube
```bash
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin
minikube start
kubectl cluster-info
```
Dashboard access:
```bash
kubectl proxy --address='0.0.0.0' --disable-filter=true
```
Open browser and put: http://YOUR_HOST_IP:8001/api/v1/namespaces/kube-system/services/http:kubernetes-dashboard:/proxy/#!/overview?namespace=default

### Jenkins image build
