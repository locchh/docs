# Compute

This category runs from **Amazon EC2**, virtual machines you size and patch
yourself, to **AWS Lambda**, which runs invoked code without servers you manage.
Between them sit **AWS Elastic Beanstalk**, which provisions and updates
an application stack for you, and **AWS Batch**, which schedules jobs onto
capacity it manages. **Elastic Load Balancing** and **Amazon EC2 Auto Scaling**
add health-based replacement and traffic distribution to applicable
instance-backed workloads.

The decision the category keeps asking you to make is how much of the stack you
want to manage. Every step toward the managed end trades configuration control
for less operational work, and the exam names the answer it wants with wording
such as "least operational overhead" or "without modifying the application". A
second decision runs alongside it in every cost question: how you pay.
On-Demand, Reserved Instances, Savings Plans and Spot each match a different mix
of predictable and interruptible.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [ec2.md](ec2.md) | Pick an instance family, a purchasing option, and a placement and networking setup for a stated workload | L |
| [ami.md](ami.md) | Build, share and expire golden images across accounts and Regions | S |
| [ec2-auto-scaling.md](ec2-auto-scaling.md) | Choose a scaling policy, and use lifecycle hooks, warm pools and instance refresh | M |
| [elastic-load-balancing.md](elastic-load-balancing.md) | Choose among Application, Network and Gateway Load Balancers, and configure targets, health checks and TLS | M |
| [lambda.md](lambda.md) | Size memory, control concurrency, and select the right invocation model and event source | L |
| [elastic-beanstalk.md](elastic-beanstalk.md) | Choose a deployment policy against downtime, rollback and cost | S |
| [batch.md](batch.md) | Run long or parallel jobs on Spot capacity without building a scheduler | S |
| [other-compute-and-end-user.md](other-compute-and-end-user.md) | Place a workload at the edge or on premises, and recognize the end-user computing services | XS group |

## Which exam tasks this serves

On SAA-C03 it is tasks 3.2 and 4.2 outright, plus task 2.1 for serverless
patterns and loose coupling and task 2.2 for fault tolerance behind a load
balancer. On SAP-C02 it is tasks 4.3 and 4.4 for platform choice and serverless
modernization, 2.1 for deployment and rollback, 2.4 and 3.4 for scaling and
reliability, 2.5 for instance families, and 1.5, 2.6 and 3.5 for purchasing
options and rightsizing.

## Reading order

Start with `ec2.md`, since the purchasing options and instance families in it
show up in every other unit. Then `ec2-auto-scaling.md` and
`elastic-load-balancing.md` as a pair, because the exam almost never tests one
without the other. Note that AWS files load balancing under networking, so look
for it here rather than in `04-networking`. Read `lambda.md` next, then
`ami.md`, `elastic-beanstalk.md` and `batch.md`. An Associate-only candidate can
skim `other-compute-and-end-user.md`, much of which is in scope for SAP-C02
only, and can skip its **Amazon Lightsail** section, bundled virtual servers at
a flat monthly price, which the SAA-C03 guide lists as out of scope.
