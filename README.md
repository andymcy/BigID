BigID DevOps Home Assignment
A small FastAPI service that returns the client's IP address. The project includes tests, Docker, a Helm chart, and a GitHub Actions pipeline.
API
Endpoint	Purpose
/	Returns the client IP as JSON
/health	Liveness check
/ready	Readiness check


The service uses the direct connection IP and does not trust forwarded IP headers by default. Behind a proxy, this may be the proxy's IP rather than the user's public IP.
Run locally
Requires Python 3.12.
python -m venv .venv
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m app.main
Open http://localhost:8000/health to check the service.

Run tests and linting:
python -m pytest -q
python -m ruff check .
Docker
docker build -t client-ip:local .
docker run --rm -p 8000:8000 client-ip:local
The image uses a multi-stage build and runs as a non-root user.
Kubernetes with Helm
Requires Docker, kind, kubectl, and Helm.
kind create cluster --name bigid
kind load docker-image client-ip:local --name bigid
helm lint ./charts/client-ip
helm upgrade --install client-ip ./charts/client-ip --namespace staging --create-namespace --set image.repository=client-ip --set image.tag=local --set image.pullPolicy=IfNotPresent
kubectl rollout status deployment/client-ip -n staging
kubectl port-forward -n staging service/client-ip 8000:80
In another terminal:
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/ready
The chart's values.yaml controls the image, replica count, probes, Service port, and CPU/memory resources. No application secrets are stored in the chart; use Kubernetes Secrets if needed.

Clean up with kind delete cluster --name bigid.
CI/CD
The workflow at .github/workflows/ci.yml runs on pushes to main, pull requests to main, and manual runs. It:
1. Runs Ruff and pytest.
2. Builds a Docker image tagged with the commit SHA.
3. Scans the image with Trivy for HIGH and CRITICAL vulnerabilities and uploads the report.
4. Validates the Helm chart.
5. Deploys to a temporary kind cluster in the staging namespace and runs smoke tests.
6. Publishes the tested image to GitHub Container Registry on successful, trusted pushes to main.
Image location: ghcr.io/andymcy/bigid:<commit-sha> (after a successful publish). The kind cluster used in CI is temporary, not a permanent staging environment.

If a pipeline job fails, scripts/diagnose_failure.py retrieves failed-job logs, redacts secrets, and requests a short diagnosis from Gemini (`gemini-3.5-flash-lite`). Add `GEMINI_API_KEY` under GitHub repository → Settings → Secrets and variables → Actions to enable this. The result is written to the workflow summary; same-repository PRs may also receive a comment. The script is not given secrets for fork PRs.

See the actual run results under the repository's Actions tab. Local and CI execution results should be verified before submission.
