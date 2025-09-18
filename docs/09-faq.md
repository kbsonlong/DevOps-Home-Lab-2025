# Frequently Asked Questions

## General Questions

### Q: What is this project?
**A:** This is a production-ready humor memory game that teaches DevOps from Docker Compose to global Kubernetes deployment. You'll learn the same infrastructure patterns used by major technology companies.

### Q: Do I need a real domain name?
**A:** No! You can complete all milestones using `kbsonlong.com` for local development. A real domain is only needed for the final global deployment milestone.

### Q: How long does this take?
**A:** Each milestone takes 30-60 minutes for beginners. The entire project takes 4-6 hours spread over multiple sessions.

### Q: What if I get stuck?
**A:** Each milestone has troubleshooting sections. If you're still stuck, check [08-troubleshooting.md](08-troubleshooting.md) for common issues and solutions.

## Technical Questions

### Q: Why use k3d instead of Docker Desktop's Kubernetes?
**A:** k3d is lighter, faster, and more reliable for learning. It's also closer to production Kubernetes environments.

### Q: What's the difference between Docker Compose and Kubernetes?
**A:** Docker Compose is for local development and simple deployments. Kubernetes is for production-scale orchestration with features like auto-scaling, rolling updates, and service discovery.

### Q: Why do I need to import images to k3d?
**A:** k3d has its own image context separate from your local Docker daemon. The `k3d image import` command ensures the cluster can access your updated images.

### Q: What if my pods keep restarting?
**A:** Check the logs with `kubectl logs <pod-name> -n humor-game`. Common causes are resource constraints, missing dependencies, or configuration errors.

## Environment Questions

### Q: Can I use Windows?
**A:** Yes, but you'll need WSL2 (Windows Subsystem for Linux) for the best experience. The commands are designed for macOS and Linux.

### Q: How much RAM do I need?
**A:** Minimum 4GB available RAM. 8GB+ is recommended for a smooth experience.

### Q: What if Docker Desktop won't start?
**A:** On macOS, you can use Colima as an alternative: `brew install colima && colima start --cpu 2 --memory 4 --disk 20`

### Q: Can I use a different Kubernetes distribution?
**A:** Yes! You can use minikube, kind, or any other local Kubernetes. Just adjust the commands accordingly.

## Application Questions

### Q: What is the humor memory game?
**A:** It's a browser-based card matching game with emojis and jokes. The game itself is simple, but the infrastructure around it is production-grade.

### Q: Why PostgreSQL and Redis?
**A:** PostgreSQL provides persistent storage for game data, while Redis provides fast caching for leaderboards and session data. This is a common production pattern.

### Q: Can I modify the game?
**A:** Absolutely! The game code is in `frontend/src/scripts/game.js`. Modify it to learn how changes propagate through the infrastructure.

### Q: What happens to my game data?
**A:** In Docker Compose, data is stored in named volumes. In Kubernetes, data is stored in PersistentVolumeClaims that survive pod restarts.

## Infrastructure Questions

### Q: What is an Ingress Controller?
**A:** An Ingress Controller routes external traffic to your services. It's like a smart reverse proxy that understands Kubernetes service discovery.

### Q: Why Prometheus and Grafana?
**A:** Prometheus collects metrics, Grafana visualizes them. Together they provide observability - the ability to see what's happening in your system.

### Q: What is GitOps?
**A:** GitOps means using Git as the single source of truth for your infrastructure. Changes to Git automatically deploy to your cluster, making deployments auditable and repeatable.

### Q: What are Network Policies?
**A:** Network Policies control which pods can communicate with each other. They provide security by isolating services and preventing unauthorized access.

## Production Questions

### Q: Is this really production-ready?
**A:** The infrastructure patterns are production-ready, but you'd need to add things like backup strategies, disaster recovery, and more comprehensive monitoring for actual production use.

### Q: Can I deploy this to the cloud?
**A:** Yes! The Kubernetes manifests work on any Kubernetes cluster - AWS EKS, Google GKE, Azure AKS, or your own cluster.

### Q: What about security?
**A:** The project includes security contexts (non-root containers), network policies, and RBAC. For production, you'd add things like image scanning, secret management, and compliance policies.

### Q: How do I scale this?
**A:** The Horizontal Pod Autoscaler (HPA) automatically scales pods based on CPU/memory usage. You can also manually scale with `kubectl scale deployment backend --replicas=5 -n humor-game`

## Troubleshooting Questions

### Q: My pods are stuck in "Pending" status
**A:** Check resource availability with `kubectl top nodes`. If resources are low, reduce cluster size or close other applications.

### Q: I can't access my application
**A:** Check if the ingress controller is running: `kubectl get pods -n ingress-nginx`. Verify your hosts file has `127.0.0.1 kbsonlong.com`.

### Q: Monitoring shows no data
**A:** Check if Prometheus is running: `kubectl get pods -n monitoring`. Generate some traffic to your application to create metrics.

### Q: ArgoCD won't sync
**A:** Check if ArgoCD can access your Git repository. Verify the repository URL and credentials in the ArgoCD UI.

## Learning Questions

### Q: What should I learn next?
**A:** After completing this project, explore service meshes (Istio), advanced monitoring (Jaeger), and cloud-native security (OPA Gatekeeper).

### Q: How do I contribute to this project?
**A:** Fork the repository, make improvements, and submit pull requests. Focus on documentation, bug fixes, or new features.

### Q: Can I use this for my own projects?
**A:** Absolutely! The infrastructure patterns are reusable. Just replace the game application with your own code.

### Q: Where can I get help?
**A:** Check the troubleshooting guide, search GitHub issues, or ask questions in the project discussions.

## Performance Questions

### Q: Why is my application slow?
**A:** Check resource usage with `kubectl top pods -n humor-game`. The application might be resource-constrained.

### Q: How do I optimize performance?
**A:** Use the monitoring dashboards to identify bottlenecks. Common optimizations include resource limits, connection pooling, and caching strategies.

### Q: What about database performance?
**A:** PostgreSQL is configured with reasonable defaults for development. For production, you'd tune connection pools, indexes, and query optimization.

### Q: How do I handle high traffic?
**A:** The HPA automatically scales pods. For extreme traffic, consider using a CDN and database read replicas.

## Still Have Questions?

1. **Check the troubleshooting guide**: [08-troubleshooting.md](08-troubleshooting.md)
2. **Review the milestone docs**: Each milestone has detailed explanations
3. **Search the code**: The code is well-commented and self-documenting
4. **Ask the community**: Use GitHub discussions or issues

Remember: There are no stupid questions! This project is designed for learning, so take your time and ask for help when you need it.
