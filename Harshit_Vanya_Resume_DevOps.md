# HARSHIT VANYA

**Senior DevOps Engineer | Cloud Infrastructure & Automation**

Bhopal, India | +91-9755106375 | harshitvanyagmer@gmail.com | [linkedin.com/in/harshit-vanya](https://linkedin.com/in/harshit-vanya) | [github.com/Harshit-Vanya](https://github.com/Harshit-Vanya)

---

## PROFESSIONAL SUMMARY

Senior DevOps Engineer with 6+ years of experience architecting, automating, and managing scalable cloud infrastructure across AWS and Azure environments. Proven track record in leading cross-functional engineering teams, designing CI/CD pipelines, implementing Infrastructure-as-Code with Ansible and Terraform, and building robust API integration platforms. Deep expertise in container orchestration (Kubernetes, Docker), Apache-based web infrastructure, and automated testing frameworks. Adept at translating business requirements into production-grade, highly available systems while mentoring engineers and driving DevOps culture adoption across organizations.

---

## KEY SKILLS

| Category | Technologies & Tools |
|----------|---------------------|
| **Infrastructure & Automation** | Ansible, Terraform, CloudFormation, Infrastructure-as-Code (IaC), Configuration Management, Server Provisioning |
| **Cloud Platforms (AWS)** | EC2, ECS, EKS, Lambda, S3, SQS, SNS, CloudWatch, IAM, Route 53, VPC, RDS, ElastiCache, CodePipeline, CodeDeploy |
| **Cloud Platforms (Azure)** | Azure Kubernetes Service (AKS), Azure DevOps, Azure Monitor, Azure Functions, ARM Templates |
| **CI/CD & Build Systems** | Jenkins, GitHub Actions, GitLab CI/CD, Azure DevOps Pipelines, ArgoCD, Spinnaker |
| **Containers & Orchestration** | Docker, Kubernetes, Helm, ECS Fargate, Docker Compose |
| **Web & API Infrastructure** | Apache HTTP Server, Nginx, Apache Kafka, REST APIs, SOAP APIs, API Gateway, Load Balancing |
| **API Testing & Quality** | Postman, Newman (CLI), pytest, Swagger/OpenAPI Validation, Contract Testing, JMeter, Locust |
| **Monitoring & Observability** | Prometheus, Grafana, ELK Stack, CloudWatch, Datadog, PagerDuty |
| **Scripting & Development** | Python, Bash, SQL, YAML, JSON, Go (basic) |
| **Other** | Git, Linux Administration, Networking (TCP/IP, DNS, SSL/TLS), Security Hardening, Agile/Scrum |

---

## WORK EXPERIENCE

### Senior DevOps Engineer / DevOps Lead — CloudNexus DigiWeb Services Pvt. Ltd.
**Mar 2024 – Present** | Bhopal, India

- Led a team of 6 engineers, coordinating task delivery, conducting code reviews, and providing technical mentorship across multiple client engagements in Agile sprints.
- Architected and maintained CI/CD pipelines using Jenkins, GitHub Actions, and Azure DevOps — reducing deployment frequency from bi-weekly to multiple daily releases with zero-downtime deployments.
- Designed and implemented Infrastructure-as-Code (IaC) using **Ansible** (50+ playbooks) and Terraform to automate provisioning of AWS EC2, EKS clusters, RDS instances, and VPC configurations across 3 environments (dev, staging, production).
- Deployed and managed **Apache HTTP Server** clusters with mod_proxy and mod_security for a GEICO enterprise client, handling 10K+ concurrent connections with automated SSL certificate rotation.
- Built an end-to-end **API testing** pipeline using Postman/Newman integrated into CI/CD, validating REST and SOAP endpoints with contract testing, achieving 95%+ API test coverage before production deployments.
- Engineered an event-driven data validation platform on **AWS** (Lambda + SQS + S3), processing 500K+ daily events with automated retry/dead-letter queue patterns and CloudWatch alerting.
- Designed and deployed containerized microservices on **Azure Kubernetes Service (AKS)** with Helm charts, implementing horizontal pod autoscaling, rolling updates, and automated rollback strategies.
- Implemented centralized logging and monitoring using ELK Stack and Prometheus/Grafana, reducing mean-time-to-detection (MTTD) by 60% and MTTR by 45%.
- Automated server configuration and application deployments using **Ansible** roles and Galaxy modules, eliminating manual SSH-based deployments and reducing provisioning time from hours to minutes.
- Established API governance standards and automated **API testing** workflows (schema validation, load testing with JMeter, security scanning with OWASP ZAP) across the organization.

### DevOps Engineer — CloudNexus DigiWeb Services Pvt. Ltd.
**Sep 2022 – Feb 2024** | Bhopal, India

- Built and maintained CI/CD pipelines for 12+ microservices using Jenkins and GitLab CI, integrating automated testing, Docker image builds, and Kubernetes deployments.
- Managed **AWS** infrastructure including EC2 fleets, Auto Scaling Groups, Application Load Balancers, and RDS clusters serving production workloads for enterprise clients.
- Configured and optimized **Apache** web servers and reverse proxies for high-traffic applications, implementing caching strategies and security hardening (mod_security, rate limiting).
- Developed **Ansible** playbooks for automated patching, compliance checks, and application deployment across 100+ Linux servers, reducing manual effort by 80%.
- Created comprehensive **API testing** suites using Postman collections and Newman CLI, integrated into pre-deployment gates in CI/CD pipelines.
- Implemented infrastructure monitoring with Prometheus, Grafana, and CloudWatch dashboards; configured alerting rules and on-call rotation with PagerDuty.
- Containerized legacy monolithic applications into Docker-based microservices and orchestrated deployments on ECS Fargate and EKS.
- Automated DNS management, SSL provisioning (Let's Encrypt/ACM), and CDN configuration for client-facing applications.

### Junior DevOps Engineer — CloudNexus DigiWeb Services Pvt. Ltd.
**Mar 2021 – Aug 2022** | Bhopal, India

- Supported infrastructure provisioning and configuration management using Ansible and AWS CloudFormation templates.
- Maintained Jenkins pipelines, troubleshot build failures, and implemented automated artifact publishing to S3 and ECR.
- Assisted in migrating on-premise workloads to AWS, including network configuration (VPC, subnets, security groups) and database migration (RDS).
- Wrote Bash and Python scripts for log rotation, backup automation, health checks, and deployment orchestration.
- Configured **Apache** virtual hosts, SSL termination, and URL rewriting for multi-tenant web applications.
- Performed **API testing** and validation using Postman during integration testing phases, documenting API contracts and edge cases.

### Software Engineering Intern — TechDrive Solutions
**Jun 2020 – Feb 2021** | Bhopal, India

- Developed RESTful APIs using Python (Flask/FastAPI) with comprehensive unit and integration test coverage.
- Participated in CI/CD pipeline setup using GitHub Actions for automated testing and deployment to AWS EC2.
- Gained foundational experience in Linux server administration, Docker containerization, and cloud-native architecture.

---

## PROJECTS

### Enterprise Infrastructure Automation Platform — Ansible + AWS + Terraform
**Duration: 8 Months**

- Designed a comprehensive infrastructure automation platform using **Ansible** (70+ roles) and Terraform modules to manage multi-account AWS environments for enterprise clients.
- Automated end-to-end server provisioning, application deployment, security hardening, and compliance auditing across 200+ EC2 instances.
- Implemented dynamic inventory management with AWS EC2 plugin, enabling automatic discovery and configuration of new instances.
- Built custom Ansible modules for proprietary API integrations, reducing onboarding time for new services from days to hours.
- Integrated with Jenkins for GitOps-driven infrastructure changes with automated plan/apply workflows and Slack notifications.

### High-Availability API Gateway & Testing Framework — AWS + Apache + CI/CD
**Duration: 6 Months**

- Architected a highly available API gateway using **Apache HTTP Server** with mod_proxy_balancer, handling 50K+ requests/minute across multiple backend microservices.
- Built a comprehensive **API testing** framework using Postman/Newman, pytest, and custom Python validators — executing 2,000+ test cases per deployment cycle.
- Implemented contract testing (consumer-driven) using Pact framework to ensure API backward compatibility across 15+ microservices.
- Configured automated performance testing using JMeter and Locust, integrated into CI/CD gates with configurable SLA thresholds.
- Deployed the platform on **AWS** ECS with Auto Scaling, Application Load Balancer, and Route 53 health checks for multi-region failover.

### Real-Time Infrastructure Monitoring & Incident Response Platform
**Duration: 5 Months**

- Built a real-time monitoring platform using Prometheus, Grafana, and ELK Stack to observe 100+ services across AWS and on-premise infrastructure.
- Streamed infrastructure metrics and application logs through **Apache Kafka** into Elasticsearch for centralized analysis and alerting.
- Developed custom Grafana dashboards and Prometheus alerting rules, reducing MTTD from 15 minutes to under 2 minutes.
- Automated incident response workflows using **Ansible** Tower (AWX) for self-healing actions (service restart, scaling, failover).
- Integrated with PagerDuty and Slack for intelligent alert routing and escalation policies.

### Cloud Migration & Containerization — On-Premise to AWS EKS
**Duration: 6 Months**

- Led migration of 8 legacy applications from on-premise servers to AWS EKS, including Dockerization, Helm chart creation, and CI/CD pipeline setup.
- Implemented blue-green and canary deployment strategies using ArgoCD and Istio service mesh.
- Designed network architecture (VPC, subnets, NACLs, security groups) and IAM policies following least-privilege principles.
- Automated the entire deployment lifecycle with **Ansible** for infrastructure provisioning and Helm/ArgoCD for application deployment.
- Achieved 99.95% uptime SLA with automated failover, horizontal pod autoscaling, and cluster autoscaler configurations.

---

## EDUCATION

**B.Tech / B.E., Computer Science and Engineering (CSE)**
Sagar Institute of Science Technology and Research, Bhopal — 2020
Grade: 7.8/10

**12th — Madhya Pradesh Board (English medium)** — 2016
Marks: 74%

**10th — Madhya Pradesh Board (English medium)** — 2014
Marks: 89%

---

## CERTIFICATIONS

- AWS Certified Solutions Architect – Associate
- AWS Certified DevOps Engineer – Professional
- Red Hat Certified System Administrator (RHCSA)
- Certified Kubernetes Administrator (CKA)
- HashiCorp Certified: Terraform Associate

---

## ACHIEVEMENTS & ADDITIONAL INFORMATION

- **Leadership Recognition:** Promoted from DevOps Engineer to DevOps Lead within 2 years for exceptional technical delivery, team mentorship, and client satisfaction.
- **Infrastructure Scale:** Managed AWS infrastructure supporting 500K+ daily API transactions and 99.9%+ uptime across production environments.
- **Cost Optimization:** Reduced AWS infrastructure costs by 35% through right-sizing, Reserved Instances, Spot Fleet adoption, and automated resource scheduling.
- **Open Source:** Active contributor to Ansible Galaxy community roles and Terraform provider modules.
- **Languages:** English, Hindi
