# Jenkins deployment for k8s and ansible
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
If you use VirtualHost without nested virtualization, then for start minikube use:
```bash
sudo minikube start --vm-driver none
sudo kubectl cluster-info
sudo kubectl proxy --address='0.0.0.0' --disable-filter=true  &
sudo minikube dashboard --url 
```
Dashboard access:
```bash
kubectl proxy --address='0.0.0.0' --disable-filter=true
```
Open browser and put: [http://YOUR_HOST_IP:8001/api/v1/namespaces/kube-system/services/http:kubernetes-dashboard:/proxy/#!/overview?namespace=default](http://YOUR_HOST_IP:8001/api/v1/namespaces/kube-system/services/http:kubernetes-dashboard:/proxy/#!/overview?namespace=default)

Check installation:
```bash
[plu@home ~]$ minikube status
There is a newer version of minikube available (v1.0.0).  Download it here:
https://github.com/kubernetes/minikube/releases/tag/v1.0.0

To disable this notification, run the following:
minikube config set WantUpdateNotification false
host: Running
kubelet: Running
apiserver: Running
kubectl: Correctly Configured: pointing to minikube-vm at 192.168.99.100

[plu@home ~]$ kubectl cluster-info
Kubernetes master is running at https://192.168.99.100:8443
KubeDNS is running at https://192.168.99.100:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

```

192.168.99.100 - will be you k8s cluster external interface

### Jenkins image build
Automated build here: 
[Docker hub url](https://cloud.docker.com/repository/docker/pluhin31/jenkins_ci/general)
