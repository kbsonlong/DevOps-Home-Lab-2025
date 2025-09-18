# Glossary

## DevOps & Infrastructure Terms

**ArgoCD**: A GitOps continuous delivery tool for Kubernetes. Automatically syncs your cluster with Git repository changes.

**ConfigMap**: A Kubernetes resource that stores non-sensitive configuration data (like environment variables) separate from your application code.

**Container**: A lightweight, isolated environment that runs your application. Think of it as a package that includes your code and all its dependencies.

**Deployment**: A Kubernetes resource that manages the deployment and scaling of a set of Pods. Ensures your application runs with the desired number of replicas.

**Docker**: A platform for developing, shipping, and running applications in containers. Provides the foundation for containerization.

**Docker Compose**: A tool for defining and running multi-container Docker applications. Uses a YAML file to configure your application's services.

**GitOps**: A way of managing infrastructure and deployments where Git is the single source of truth. Changes to Git automatically deploy to your infrastructure.

**Horizontal Pod Autoscaler (HPA)**: A Kubernetes resource that automatically scales the number of pods based on CPU or memory usage.

**Ingress**: A Kubernetes resource that manages external access to services in your cluster, typically HTTP/HTTPS. Acts like a smart reverse proxy.

**Ingress Controller**: The actual implementation of the Ingress resource. Handles the routing of external traffic to your services.

**k3d**: A lightweight tool for running k3s (a lightweight Kubernetes distribution) in Docker. Perfect for local development and learning.

**Kubernetes (K8s)**: An open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications.

**Namespace**: A way to organize resources within a Kubernetes cluster. Like folders in a file system, but for Kubernetes resources.

**Network Policy**: A Kubernetes resource that controls how pods communicate with each other. Provides network-level security and isolation.

**PersistentVolumeClaim (PVC)**: A request for storage by a user. Allows pods to use persistent storage that survives pod restarts.

**Pod**: The smallest deployable unit in Kubernetes. A Pod contains one or more containers and shares network and storage resources.

**Secret**: A Kubernetes resource that stores sensitive data like passwords, API keys, and certificates. Data is base64 encoded.

**Service**: A Kubernetes resource that defines a logical set of Pods and a policy for accessing them. Provides stable networking for your application.

**ServiceAccount**: A Kubernetes resource that provides an identity for processes running in a Pod. Used for authentication and authorization.

## Application Terms

**API**: Application Programming Interface. A set of rules that allows one application to communicate with another. Your backend provides APIs for the frontend.

**Backend**: The server-side part of your application that handles business logic, database operations, and provides APIs.

**Frontend**: The client-side part of your application that users interact with. In this project, it's a web-based game interface.

**Health Check**: A way to determine if your application is working correctly. Kubernetes uses health checks to know when to restart pods.

**Load Balancer**: A component that distributes incoming network traffic across multiple servers or pods to ensure no single server becomes overwhelmed.

**Reverse Proxy**: A server that sits between clients and backend servers, forwarding requests and responses. Nginx acts as a reverse proxy in this project.

## Database Terms

**PostgreSQL**: A powerful, open-source relational database system. Stores your game data persistently.

**Redis**: An in-memory data structure store used as a database, cache, and message broker. Provides fast access to frequently used data.

**Connection Pool**: A cache of database connections maintained so that the connections can be reused when future requests to the database are required.

## Monitoring Terms

**Grafana**: An open-source analytics and visualization platform. Creates dashboards from your metrics data.

**Metrics**: Numerical data that describes your system's behavior over time. Examples include CPU usage, memory consumption, and request rates.

**Observability**: The ability to understand the internal state of a system by examining its outputs. Composed of metrics, logs, and traces.

**Prometheus**: An open-source monitoring system that collects and stores metrics. Pulls data from your applications and infrastructure.

**RBAC**: Role-Based Access Control. A method of regulating access to computer or network resources based on the roles of individual users.

## Networking Terms

**ClusterIP**: A type of Kubernetes Service that exposes the service on a cluster-internal IP. Only accessible from within the cluster.

**DNS**: Domain Name System. Translates human-readable domain names (like kbsonlong.com) into IP addresses.

**LoadBalancer**: A type of Kubernetes Service that exposes the service externally using the cloud provider's load balancer.

**NodePort**: A type of Kubernetes Service that exposes the service on the same port of each selected Node in the cluster.

**Port**: A communication endpoint in networking. Your backend runs on port 3001, frontend on port 80, etc.

## Security Terms

**Base64**: A group of binary-to-text encoding schemes that represent binary data in an ASCII string format. Used to encode secrets in Kubernetes.

**JWT**: JSON Web Token. A compact, URL-safe means of representing claims to be transferred between two parties.

**Non-root**: Running a container as a user other than root (UID 0). A security best practice that limits the damage if a container is compromised.

**Security Context**: Kubernetes configuration that controls security settings for a Pod or Container, such as user ID, group ID, and capabilities.

**TLS**: Transport Layer Security. A cryptographic protocol that provides secure communication over a computer network. Used for HTTPS.

## Development Terms

**Environment Variable**: A variable whose value is set outside the application, typically through configuration files or the operating system.

**Git**: A distributed version control system that tracks changes in source code during software development.

**Helm**: A package manager for Kubernetes that simplifies the deployment and management of applications.

**kubectl**: The command-line tool for interacting with Kubernetes clusters. Used to deploy applications, inspect resources, and manage clusters.

**YAML**: A human-readable data serialization format commonly used for configuration files. Kubernetes manifests are written in YAML.

## Production Terms

**Auto-scaling**: The ability to automatically increase or decrease the number of resources (like pods) based on demand.

**Blue-Green Deployment**: A deployment strategy that reduces downtime and risk by running two identical production environments.

**Canary Deployment**: A deployment strategy where a new version is deployed to a small subset of users before rolling out to everyone.

**CDN**: Content Delivery Network. A distributed network of servers that delivers content to users based on their geographic location.

**Rolling Update**: A deployment strategy where new versions are deployed gradually, replacing old versions one at a time.

**Zero-downtime Deployment**: A deployment strategy that ensures your application remains available during updates.

## Still Confused?

If you encounter a term that's not in this glossary:

1. **Check the milestone docs**: Each milestone explains the terms it introduces
2. **Search online**: Many terms have excellent explanations on sites like Wikipedia
3. **Ask questions**: Use the FAQ or troubleshooting guides for clarification

Remember: Learning new terminology is part of the journey. Don't worry if you don't understand everything immediately!
