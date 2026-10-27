---
type: Concept
title: "ACAP SDK tools: train-tensorflow-model-using-aws (Ansible EC2 training)"
description: "How the train-tensorflow-model-using-aws tool provisions an AWS GPU instance with Ansible, runs the tensorflow-to-larod-artpec8 training and conversion, fetches converted_model.tflite and terminates the instance, with variables, security model, cost leaks and the defects that block the documented run."
tags: [edge-ai, axis, acap, training, aws, ansible, tensorflow, docker, security]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-08-31
sources:
  - id: sdk-tools-readme
    resource: ../raw/acap-sdk-tools/README.md
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746d39fb25384402d0f900eb5a6a27c29d69 (2026-08-18)"
    title: "AxisCommunications/acap-sdk-tools — root README (git submodule)"
  - id: aws-readme
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/README.md
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "train-tensorflow-model-using-aws README"
  - id: aws-playbook
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/playbooks/deploy.yaml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Ansible playbook deploy.yaml"
  - id: aws-vars
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/inventory/group_vars/vars.yaml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "group_vars/vars.yaml"
  - id: aws-inventory
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/inventory/inventory_aws_ec2.yaml
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Dynamic inventory inventory_aws_ec2.yaml"
  - id: aws-ansible-cfg
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/ansible.cfg
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "ansible.cfg"
  - id: aws-dockerfile
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/Dockerfile
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Ansible runner Dockerfile"
  - id: aws-diagram
    resource: ../raw/acap-sdk-tools/train-tensorflow-model-using-aws/data/security_diagram.svg
    scope: ../raw/acap-sdk-tools/
    kind: image
    revision: "7250746"
    title: "security_diagram.svg — IAM and key-pair authorization diagram"
---

# ACAP SDK tools: train-tensorflow-model-using-aws (Ansible EC2 training)

This tool automates the training half of the `tensorflow-to-larod-artpec8` example: an Ansible playbook, run from a small Docker container on the developer machine, starts one GPU EC2 instance in AWS, copies the training example to it, runs the example's environment build, training and conversion, fetches `converted_model.tflite` back, and terminates the instance.[^aws-readme] It is the second tool in the [acap-sdk-tools repository](acap-sdk-tools-repository.md).[^sdk-tools-readme] The tool contains no model code: architecture, dataset and conversion come from the external training example, summarised in [tensorflow-to-larod training and conversion guides](acap-example-model-training-guides.md). Findings are **Observed** by static reading of the files unless marked **Reported** (README) or *Synthesis*; nothing was run and no AWS call was made.

## Architecture and data flow

```text
developer machine (Docker: Ansible 5.0.1) ──IAM keys──▶ AWS EC2 API
        │                                              creates SG + g4dn instance
        └──────── SSH :22 (key pair, SG limited to caller /32) ──▶ EC2 "training"
                                   copy example → build_env.sh → docker train + convert
        ◀──────── fetch converted_model.tflite ───────────────────  then terminate
```

The playbook has three plays.[^aws-playbook]

| Play | Tags | What it does |
| --- | --- | --- |
| EC2 instance deployment (`localhost`) | `creating`, `info` | Looks up the caller's public IP with `ipify_facts`; ensures a security group named by `security_group` allowing only TCP/22 from that IP/32; starts one tagged instance with the configured type and AMI and waits; prints IP and DNS; `add_host` to group `aws_ec2`; appends the host key with `ssh-keyscan` to `~/.ssh/known_hosts` |
| Training pipeline (`aws_ec2`, user `ubuntu`) | `training` | Copies `EXAMPLE_DIRECTORY` to `/home/ubuntu`; runs `cd tensorflow-to-larod-artpec8 && chmod +x build_env.sh && ./build_env.sh`; runs `docker run --gpus all -dit --name training tensorflow-to-larod-a8`, `training/train.py -i data/images/val2017/ -a data/annotations/instances_val2017.json`, `convert_model.py -i models/trained_model.pb -o app/converted_model.tflite` and `docker cp`; `fetch`es the `.tflite` to `/app/converted_model.tflite` (also tagged `cleanup`) |
| Cleanup (`localhost`) | `cleanup` | Lists running instances tagged `user=<user>` in the region, terminates each, removes their entries from `known_hosts` |

No S3 bucket, EBS snapshot, VPC, subnet or IAM resource is created: the default VPC is used, and the IAM user, access keys and key pair are manual prerequisites. The README's "Network configuration" section only lists, as optional steps, the Ansible modules one would use to build a custom VPC.[^aws-readme]

## Prerequisites and commands (Reported)

Ansible 5 with `community.aws` and an AWS account. The README walks through an IAM group with `AmazonEC2FullAccess`, an IAM user named like the local `$USER` with programmatic access keys exported as `AWS_ACCESS_KEY`/`AWS_SECRET_KEY`, a key pair named `$USER-key-pair` saved as `.pem` in the working directory (`chmod 400`), and editing `EXAMPLE_DIRECTORY` and the `<USER>` placeholder in the inventory.[^aws-readme] The run is:

```sh
docker build --build-arg AWS_ACCESS_KEY="${AWS_ACCESS_KEY:-}" \
  --build-arg AWS_SECRET_KEY="${AWS_SECRET_KEY:-}" --build-arg USER="${USER:-}" -t <APP_IMAGE> .
docker run -it --name <APP_CONTAINER> <APP_IMAGE>
docker cp <APP_CONTAINER>:/app/converted_model.tflite .
```

If training fails before cleanup, the README's recovery command is `ansible-playbook playbooks/deploy.yaml --private-key $USER-key-pair.pem --tags cleanup`.[^aws-readme] The training example must be copied into the working directory first, otherwise Docker cannot find it.

## Variables

Defaults in `inventory/group_vars/vars.yaml`:[^aws-vars]

| Key | Default |
| --- | --- |
| `EXAMPLE_DIRECTORY` | `$HOME/acap-native-sdk-examples/tensorflow-to-larod-artpec8` |
| `aws_region` | `us-east-1` |
| `user` | `$USER` |
| `key_pair_name` | `$USER-key-pair` |
| `security_group` | `$USER-sg` |
| `instance_name` | `training-$USER` |
| `instance_type` | `g4dn.8xlarge` (hourly GPU billing; the README defers pricing to AWS) |
| `image_id` | `ami-0906aa26fea6a7007` — commented "Deep Learning Base AMI (Ubuntu 18.04) Version 44.0" |

The dynamic inventory uses the `aws_ec2` plugin for `us-east-1`, filtered to `running` instances with tag `user` equal to a literal `<USER>` placeholder that the user must replace.[^aws-inventory] `ansible.cfg` sets `remote_user = ubuntu`, `host_key_checking = False`, `deprecation_warnings = False` and a 5-second SSH keep-alive.[^aws-ansible-cfg]

## Security model

The diagram shows two authorization gates: the user's computer (Ansible environment) needs valid IAM credentials to reach AWS, then a security-group condition and a valid key pair to reach the EC2 "Training" instance inside the VPC.[^aws-diagram] In the playbook only SSH from the caller's /32 is open and no training port is exposed.[^aws-playbook] Weaknesses (**Observed**):

- Credentials are passed as `--build-arg` and stored with `ENV AWS_ACCESS_KEY`/`AWS_SECRET_KEY` in the image, so they persist in image history and the container environment.[^aws-dockerfile] No secret is committed in the repository.
- `host_key_checking` is disabled in `ansible.cfg` and on `add_host`, which makes the `ssh-keyscan`/`known_hosts` steps largely cosmetic and permits man-in-the-middle on first connection.[^aws-ansible-cfg][^aws-playbook]
- The README names the variables `AWS_ACCESS_KEY` and `AWS_SECRET_KEY`, whereas the common boto3 names are `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`; whether the Ansible modules honour the former is not shown in the repo (*Synthesis*: authentication may fail unless a mapping exists elsewhere).
- Recommended IAM policy `AmazonEC2FullAccess` is broad for this purpose.[^aws-readme]

## Cost and cleanup behaviour

A normal run ends by terminating the instance, which is the main cost control.[^aws-playbook] Leaks and hazards:

- The security group is never deleted.
- The cleanup play terminates **every** running instance tagged `user=$USER` in the region, not only the one just created.
- There is no TTL, budget alarm or error handling; the training step is one multi-command `shell` without `set -e`, and an interrupted run leaves the instance running until the `cleanup` tag is run by hand.
- A `key_name` argument is passed to the terminate task though it is irrelevant there.

## Defects that conflict with the documentation

All **Observed** except where noted.

1. `CMD ["ansible-playbook playbooks/deploy.yaml --private-key $USER-key-pair.pem"]` is exec-form with a single string, so no shell expands `$USER` and the whole string is looked up as one executable; the documented `docker run` therefore likely fails (*Synthesis* on the runtime outcome).[^aws-dockerfile]
2. The base image is `arm64v8/ubuntu:22.04`, forcing an ARM image (emulated on x86 hosts) for a tool that only needs Ansible.[^aws-dockerfile]
3. The copy task uses `src: "/app/{{ EXAMPLE_DIRECTORY }}"` while the default `EXAMPLE_DIRECTORY` already begins with `$HOME`, producing `/app/<home>/…`; the README says to place the example in the working directory instead.[^aws-playbook][^aws-vars]
4. Directory name `tensorflow-to-larod-artpec8` and image name `tensorflow-to-larod-a8` are hard-coded in three tasks, so changing `EXAMPLE_DIRECTORY` alone is insufficient; the README says only "some tasks" must change.[^aws-playbook][^aws-readme]
5. Region lives in two files (`aws_region`, inventory `regions`) and must be changed in both.[^aws-vars][^aws-inventory]
6. Version drift: `ansible==5.0.1` (2021), the short module names `ec2_group`/`ec2_instance`/`ec2_instance_info` and `ipify_facts` with no `collections:` key, a 2022-era Ubuntu 18.04 Deep Learning AMI whose current availability was not checked.[^aws-dockerfile][^aws-playbook]
7. The README's structure tree omits `data/` (`security_diagram.svg`).[^aws-readme]

## Relationships

- **Part of** [ACAP SDK tools repository](acap-sdk-tools-repository.md); its build check is in [ACAP SDK tools CI and maintenance](acap-sdk-tools-ci-and-maintenance.md).
- **Depends on** the training example documented in [tensorflow-to-larod training and conversion guides](acap-example-model-training-guides.md) (ARTPEC-8, TensorFlow 1.15 route); the result is consumed by [Larod inference](acap-example-larod-object-detection.md) and by the [custom model deployment](axis-custom-model-deployment.md) route. (*Synthesis*: this tool does not verify the model.)
- **Does not cover** ARTPEC-9, where the example directory is only a pointer; see [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md). (*Synthesis* from the hard-coded `artpec8` paths.)
- **Distinct from** [the camera calibration tool](acap-sdk-tools-camera-calibration-tool.md).

## Coverage and limits

Inspected: README, the playbook, vars, inventory, `ansible.cfg`, Dockerfile and the text labels of `security_diagram.svg`. Not available locally: the external `acap-native-sdk-examples/tensorflow-to-larod-artpec8` example (a sibling is in `raw/acap-native-sdk-examples/`), AWS service behaviour, AMI availability, current Ansible collection versions. Pricing and quotas are outside the source.

[^sdk-tools-readme]: Root README, §Tools (list entry for `train-tensorflow-model-using-aws`); revision 7250746.
[^aws-readme]: Tool README: intro, §Requirements, §Quicksteps (Initial configuration steps 1–8; Building environment 1–3), §Playbook explanation (steps 1–12, tag `cleanup`), §Variable configuration, §Network configuration, §Structure of this tool.
[^aws-playbook]: `playbooks/deploy.yaml`: play 1 lines 1–56, play 2 lines 58–92 (copy at ~69, train block 79–86, fetch 88–92), play 3 lines 94–126.
[^aws-vars]: `inventory/group_vars/vars.yaml` lines 3–11.
[^aws-inventory]: `inventory/inventory_aws_ec2.yaml` lines 1–7 (`plugin`, `regions`, `filters`).
[^aws-ansible-cfg]: `ansible.cfg`, `[defaults]` keys `host_key_checking`, `remote_user`, `deprecation_warnings`, `inventory`; `[ssh_connection]` `ssh_args`.
[^aws-dockerfile]: `train-tensorflow-model-using-aws/Dockerfile`: `FROM`, `ARG`/`ENV` lines 3–8, `pip3 install ansible==5.0.1`, `CMD`.
[^aws-diagram]: `data/security_diagram.svg`, text labels ("User computer", "Valid IAM credentials?", "Security group conditions?", "Valid key-pair?", "EC2 Instance — Training"); several labels are truncated in the source and the drawing's geometry was not rendered.
