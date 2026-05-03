# NoteVault 📚

A production-deployed, multi-user notes application built with a full DevOps pipeline — from infrastructure provisioning to automated deployments.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC)
![Ansible](https://img.shields.io/badge/Config-Ansible-EE0000)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)
![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900)

---

## What This Project Demonstrates

This isn't just a web app — it's a full DevOps workflow built around a simple Flask application:

| Layer | Tool | What it does |
|---|---|---|
| Application | Python + Flask | Multi-user notes with auth, search, pinning |
| Containerization | Docker + Docker Compose | Multistage build, optimized image |
| Infrastructure | Terraform | EC2, VPC, Security Groups on AWS |
| Configuration | Ansible | Server setup, Docker install, app deployment |
| CI/CD | GitHub Actions | Lint → Test → Build → Push → Deploy |
| Security | Trivy | Container image vulnerability scanning |

---

## Architecture

```
GitHub Push
    │
    ▼
┌─────────────────────────────────────┐
│         GitHub Actions Pipeline      │
│  lint → test → build → scan → push  │
└──────────────────┬──────────────────┘
                   │ Docker image → Docker Hub
                   ▼
┌─────────────────────────────────────┐
│           AWS (ap-south-1)           │
│                                      │
│  ┌─────────┐     ┌────────────────┐ │
│  │ Terraform│────▶│  EC2 Instance  │ │
│  │  (IaC)  │     │                │ │
│  └─────────┘     │  Ansible ────▶ │ │
│                  │  configures    │ │
│                  │  Docker +      │ │
│                  │  pulls image   │ │
│                  └────────────────┘ │
└─────────────────────────────────────┘
```

---

## Repository Structure

```
my-notes-app/
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions pipeline
├── ansible/
│   ├── inventory/                # EC2 host inventory
│   ├── playbooks/                # Server setup + deployment playbooks
│   └── roles/                    # Reusable Ansible roles
├── app/
│   ├── app.py                    # Flask app + routing
│   ├── models.py                 # SQLAlchemy models (User, Note)
│   ├── requirements.txt          # Python dependencies
│   ├── static/style.css          # Custom CSS
│   └── templates/                # Jinja2 HTML templates
├── docker/
│   ├── Dockerfile                # Single-stage build
│   └── Dockerfile.multistage     # Optimized multistage build
├── terraform/
│   ├── main.tf                   # EC2 + VPC + Security Group resources
│   ├── variables.tf              # Input variables
│   ├── outputs.tf                # EC2 public IP output
│   └── terraform.tfvars          # Variable values (not committed)
├── docker-compose.yml            # Local development compose
├── .dockerignore
├── .trivyignore                  # Trivy scan exceptions
└── .flake8                       # Python linting config
```

---

## CI/CD Pipeline (GitHub Actions)

On every push to `main`:

1. **Lint** — flake8 checks Python code style
2. **Test** — runs unit tests
3. **Build** — builds Docker image using multistage Dockerfile
4. **Scan** — Trivy scans image for vulnerabilities
5. **Push** — pushes image to Docker Hub
6. **Deploy** — Ansible pulls the new image on EC2 and restarts the container

Secrets managed via GitHub Actions secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `EC2_SSH_KEY`, `EC2_HOST`.

---

## Infrastructure (Terraform)

Provisions on AWS `ap-south-1`:

- VPC with public subnet
- EC2 instance (Ubuntu)
- Security Group (ports 22, 80, 5000)
- Outputs EC2 public IP for Ansible inventory

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Configuration Management (Ansible)

After Terraform provisions the EC2 instance, Ansible:

- Installs Docker and dependencies
- Pulls the latest image from Docker Hub
- Runs the container with correct port and volume mappings

```bash
cd ansible
ansible-playbook -i inventory/hosts playbooks/deploy.yml
```

---

## Application Features

- 🔐 User registration & login — each user sees **only their own notes**
- ✏️ Create, view, edit, and delete notes
- 📌 Pin important notes to the top
- 🏷️ Custom categories with sidebar filtering
- 🔍 Full-text search across title and content
- 📊 Live word & character count in editor
- 📱 Responsive design — mobile friendly

---

## Running Locally

### With Docker Compose (Recommended)

```bash
docker compose up -d --build
# Open: http://localhost:5000
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
python app/app.py
# Open: http://127.0.0.1:5000
```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| GET/POST | `/register` | Create a new account |
| GET/POST | `/login` | Log in |
| GET | `/logout` | Log out |
| GET | `/` | Dashboard (search & filter) |
| GET/POST | `/note/add` | Create a note |
| GET | `/note/<id>` | View a note |
| GET/POST | `/note/<id>/edit` | Edit a note |
| POST | `/note/<id>/delete` | Delete a note |
| POST | `/note/<id>/pin` | Toggle pin |

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Flask 3.0 |
| Database | SQLite via SQLAlchemy |
| Auth | Flask-Login + Werkzeug |
| Container | Docker (multistage) |
| Orchestration | Docker Compose |
| IaC | Terraform |
| Config Mgmt | Ansible |
| CI/CD | GitHub Actions |
| Registry | Docker Hub |
| Cloud | AWS EC2 (ap-south-1) |
| Security Scan | Trivy |

## Contributing
 
Contributions are welcome — whether it's fixing a bug, improving the pipeline, or suggesting infrastructure improvements.
 
### How to contribute
 
1. **Fork** the repository
2. **Create a branch** for your change
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit with a clear message
   ```bash
   git commit -m "feat: describe what you changed"
   ```
4. **Push** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** against `main` with a description of what you changed and why

## Connect
 
Modified and maintained by **Manish** — actively learning and building in the DevOps and cloud space.
 
- 💼 [LinkedIn](https://www.linkedin.com/in/kumar05/) — connect if you're working on similar projects or want to discuss DevOps
- 🐙 [GitHub](https://github.com/Manish12588) — see other projects
  
If this project helped you learn something or gave you ideas, a ⭐ on the repo is appreciated.
