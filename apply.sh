#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting RBAC deployment"

# Apply rolesets first (ClusterRoles)
echo "📋 Applying rolesets..."
kubectl apply -k rolesets/

# Apply production RBAC configuration
echo "🔐 Applying production RBAC..."
kubectl apply -k clusters/production/

echo "✅ RBAC deployment completed!"
echo "📊 Current RoleBindings:"
kubectl get rolebindings --all-namespaces | grep -vE 'kube-system|kube-public|kube-node-lease'
