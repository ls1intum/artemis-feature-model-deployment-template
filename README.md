# Artemis Feature Model Deployment Template

Create your own deployment repository from this template. It receives the remote deployment packages that the
Artemis Feature Model publishes and deploys each of them to the VM of its target with GitHub Actions.

## How it works

On the review page of the feature model configurator, an administrator chooses a target name and this repository,
then deploys. The feature model application commits the generated package to the `deployment` branch, under
`deployments/<target>/package/`. That push starts the **Deploy package** workflow, which runs inside the GitHub
Environment with the same name as the target. The Environment holds everything the deployment needs: how to reach
the VM and the values the package refers to. The package itself contains no values, only variable names.

| Part | Role |
|---|---|
| `deployment-repository.json` | Declares this repository as a deployment repository. The feature model only publishes into repositories that contain it. |
| `.github/workflows/deploy.yml` | Deploys a published package to the VM of its target. |
| `.github/workflows/check-connection.yml` | Checks that the runner reaches a target's VM and reports its host keys. |
| `scripts/` | Shell and Python steps of the two workflows. |
| `requirements.txt` | Pinned Ansible toolchain of the runner. |

## Create your repository

Use **Use this template** on GitHub. The repository can be private or public, because published packages contain no
values. Your copy starts with only the `main` branch; the first publish creates the `deployment` branch.

## Let the feature model publish

The feature model application pushes with a token that it reads from the environment variable
`FM_DEPLOYMENT_REPO_TOKEN`. Create a fine-grained personal access token:

- **Resource owner**: the owner of your repository.
- **Repository access**: only select repositories, and select only this repository.
- **Repository permissions**: Contents, read and write. GitHub adds Metadata, read-only, by itself.

Set the token as `FM_DEPLOYMENT_REPO_TOKEN` in the environment where the feature model application runs, and restart
it. The token never goes into the review page or into a repository. If your repository belongs to an organization,
the organization may have to approve the token first.

On the review page, enter this repository's `https://` URL, for example `https://github.com/<owner>/<repository>.git`.

## Create one Environment per target

In **Settings → Environments**, create an Environment whose name equals the target name, for example `test-vm`.
If you publish to a new target first, GitHub creates the Environment empty, and the first run lists every value it
still needs. The Environment needs two kinds of values.

**Connection values** are the same for every package:

| Name | Set as | Description |
|---|---|---|
| `VM_HOST` | variable | Host name or address of the VM, as the runner or the jump host reaches it. |
| `VM_USERNAME` | variable | User on the VM that runs the deployment. |
| `VM_SSH_PRIVATE_KEY` | secret | Private SSH key of that user. |
| `SSH_KNOWN_HOSTS` | variable | Host keys of the VM and of the jump host, as `known_hosts` lines. Run **Check connection** in scan mode to get them. |
| `DEPLOYMENT_GATEWAY_HOST` | variable | Optional jump host. Leave it unset to connect to the VM directly. |
| `DEPLOYMENT_GATEWAY_PORT` | variable | Optional SSH port of the jump host. |
| `DEPLOYMENT_GATEWAY_USER` | variable | Optional user on the jump host. |
| `DEPLOYMENT_GATEWAY_SSH_KEY` | secret | Private SSH key for the jump host; required when `DEPLOYMENT_GATEWAY_HOST` is set. |

The jump host values can also be set once for the repository or the organization instead of per Environment.

**Package values** depend on the features you selected: an integration such as Iris adds its own values. Every
published package lists the values it needs, with a description and whether each one is a secret or a variable, in
the "Environment values" section of its `README.md` and in `metadata/env-references.json`. When a connection value
or a package value is missing, the deployment stops before it touches the VM, and the run summary lists every missing
value with its description.

## Publish

In the configurator's review page, choose **Remote server (Ansible)**, enter the target name and this repository's
URL, and select **Deploy to &lt;target&gt;**. The button publishes the package and downloads the same package as a
ZIP file. The page shows the commit that carries the package.

## After a publish

The publish starts **Deploy package** on the `deployment` branch; follow it in the **Actions** tab. The workflow
installs the pinned Ansible collection, checks that every package value is set, checks the TLS certificate on the
VM, runs the playbook, and finally waits until Artemis reports ready with the selected configuration.

- **Missing values**: add them to the Environment, then re-run the failed run.
- **Deploy the same package again**: run **Deploy package** manually on the `deployment` branch with the target name.
- **Several targets**: each target deploys in its own Environment. Different targets deploy in parallel, and runs for
  the same target wait for each other.
- **Remove a target**: delete its directory under `deployments/` on the `deployment` branch. The run that follows
  ends without deploying.

## Keep your copy up to date

A repository created from a template does not receive later changes of the template. To take them over, copy the
changed files into your `main` branch, then merge `main` into `deployment`: the workflows run from the `deployment`
branch. The feature model application only writes below `deployments/`, so this merge does not conflict with
published packages.

`deployment-repository.json` records which package format the workflow understands. When the feature model
application starts publishing a newer format, it refuses to publish into an older copy and asks you to update the
workflow and the marker from this template. The workflow also names every secret a package can use, because GitHub
holds workflows that read all secrets at once. When a newer package needs a secret your copy does not know, the run
stops before deploying and asks you to update the workflow from this template.

## VM prerequisites

- Docker, git, and the `acl` package are installed.
- GitHub-hosted runners reach the VM over SSH, directly or through the jump host.
- The deployment user can run `sudo` without a password.
- The TLS certificate and key that the package values `PROXY_SSL_CERTIFICATE_PATH` and
  `PROXY_SSL_CERTIFICATE_KEY_PATH` name exist on the VM and cover `SERVER_HOSTNAME`.
