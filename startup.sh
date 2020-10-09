#!/bin/bash
if [ "$1" == "" -a "$2" == "" ]; then
    echo "EKS Cluster name or Role name is missing" >> /var/app/startup.log
    exit 1
else
    echo "Updating the kubecontext for the cluster $1 with role name $2" >> /var/app/startup.log
    aws eks update-kubeconfig --name $1 --role $2 --region ap-southeast-2
   
fi
python3 main.py
