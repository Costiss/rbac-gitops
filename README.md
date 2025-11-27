# Kubernetes GitOps RBAC Management

# 📋 Project Overview

This repository manages Role-Based Access Control (RBAC) for Kubernetes clusters
using GitOps principles. It provides fine-grained user access control across
multiple namespaces and clusters through declarative YAML configurations.

# 🗂️ Project Structure

```bash
├── apply.sh                                # Apply RBAC configurations to clusters
├── check.py                                # Naming convention and configuration linter
├── clusters/                               # Cluster-specific configurations
│   └── production/                         # Production cluster RBAC
│       ├── kustomization.yml
│       └── namespaces/                     # Namespace-specific configurations
│           └── namespace/                  # Integrations namespace
│               ├── kustomization.yml
│               ├── namespace.yml           # Namespace definition
│               └── name-lastname.yml       # user-specific rbac bindings for namspace
│
├── rolesets/                               # Reusable RBAC role definitions
│   ├── admin-roleset.yml                   # Full administrative permissions
│   ├── developer-roleset.yml               # Developer-level permissions
│   ├── kustomization.yml                   # Rolesets kustomization
│   └── viewer-roleset.yml                  # Read-only permissions
```

# 🎯 Key Components

## 1. Rolesets (rolesets/)

Reusable ClusterRole definitions that define permission sets:

- `admin-roleset`: Full cluster/namespace administration
- `developer-roleset`: Development and deployment permissions
- `viewer-roleset`: Read-only access for monitoring

## 2. Cluster Configurations (clusters/)

Cluster-specific RBAC implementations:

Each cluster contains namespace-specific user bindings

## 3. Namespace Management (clusters/\*/namespaces/)

Fine-grained access control per namespace:

- Each namespace has its own `kustomization.yml` to aggregate user bindings.
- User-specific YAML files bind users to rolesets within that namespace.

_Obs: User files should follow the `name-lastname.yml` naming convention._

# 🛠️ Usage

## Adding New Users

### Step 1: Create User Binding File

Create a new file in the appropriate namespace directory, following the `name-lastname.yml` convention.

For demonstration we will use the namespace `payments` in the `production` cluster and add user

Example: `clusters/production/namespaces/payments/john-doe.yml`

```yml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: "john.doe"
subjects:
  - kind: User
    name: john.doe@company.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer-roleset # rolesets/developer-roleset.yml
  apiGroup: rbac.authorization.k8s.io
```

Or for more specific permissions:

```yml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: "john.doe"
rules:
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "patch"] # No delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: "john.doe"
subjects:
  - kind: User
    name: john.doe@company.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: "john.doe"
  apiGroup: rbac.authorization.k8s.io
```

### Step 2: Update Kustomization

```yml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: payments

resources:
  - namespace.yml
  - user-name.yml
  - other-user.yml
  - john-doe.yml # Add new file
```
