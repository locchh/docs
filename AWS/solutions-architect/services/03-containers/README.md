# Containers

Two services run containers on AWS, and one registry stores the images they run.
**Amazon ECS** is the AWS-native orchestrator, with its own task and service
model and no control plane for you to operate. **Amazon EKS** runs upstream
Kubernetes, so the API, the manifests and the ecosystem tooling are the ones a
Kubernetes team already has. **Amazon ECR** is the private container registry
both of them pull from, and **AWS Fargate** is the capacity mode that runs a
task without an instance you can log in to.

The category asks two related decisions, and the exam separates them carefully.
The first is which control plane: ECS when the team has no Kubernetes investment
and wants the smallest surface to operate, EKS when portability, an existing
Kubernetes skill set, or a specific Kubernetes-only add-on is a stated
requirement. The second is who runs the data plane: Fargate when the answer must
have the least operational overhead and per-task isolation, **Amazon EC2**,
virtual machines you manage yourself, when the workload needs a GPU, a specific
instance type, a daemon on the host, or the price of reserved capacity. A
question that says "no servers to manage" is pointing at Fargate, not at a
choice between ECS and EKS.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [ecs-and-ecr.md](ecs-and-ecr.md) | Write a task definition, choose a launch type and networking mode, separate task roles from execution roles, and manage images with lifecycle policies and scanning | M |
| [eks.md](eks.md) | Choose a node type, give pods their own identity and network interfaces, attach storage and load balancing, and say when EKS beats ECS | M |

## Which exam tasks this serves

On SAA-C03 it is tasks 2.1 and 3.2, both of which name container orchestration
with ECS and EKS directly, and task 2.1 also covers migrating an application
into containers and deciding when containers are the right answer at all.
Containers carry cost weight in task 4.2, where consolidating workloads onto
shared capacity is one of the named optimizations. On SAP-C02 it is task 4.3 for
selecting a container hosting platform and task 4.4 for selecting a container
service during modernization, with task 2.1 for deployment strategy, including
blue/green rollouts, and task 1.1, which names AWS container services in its
networking knowledge list.

## Reading order

Read `ecs-and-ecr.md` first. Its vocabulary, task definition, service, launch
type, capacity provider, and its split between the task role and the execution
role, is what most exam questions in this category are written in, and the
registry material applies to EKS unchanged. Then read `eks.md`, which assumes
you know that vocabulary and spends its length on what differs. An
Associate-only candidate should still read both, since SAA-C03 names ECS and EKS
in two separate task statements, but can skim the EKS Anywhere, EKS Distro and
ECS Anywhere material, which belongs to hybrid scenarios on SAP-C02.
