# Migration

This is the smallest category by unit count and one of the heaviest on SAP-C02,
where migration and modernization is a full 20 percent domain. Three units cover
it. **AWS Migration Hub** tracks a portfolio of applications through the move
and recommends a strategy for each. **AWS Application Migration Service** lifts
running servers onto **Amazon EC2**, AWS virtual machines, by block-level
replication. **AWS DMS**, the Database Migration Service, moves data between
database engines while the source stays online, with the **AWS Schema Conversion
Tool** handling the schema when the engines differ.

The decision the category keeps asking you to make is how much you change the
workload on the way over. The seven common migration strategies, the 7Rs, are
the frame: rehost with no change, replatform with a managed service underneath,
repurchase onto SaaS, refactor into a different architecture, relocate a whole
hypervisor estate, retire, and retain. Each step up costs more effort before
cutover and less operating effort after, and the exam decides between them with
the constraints in the stem: a fixed deadline pushes toward rehost, an
unsupported operating system or license cost pushes toward replatform, and a
stated scaling or agility goal pushes toward refactor.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [migration-hub-discovery-and-strategy.md](migration-hub-discovery-and-strategy.md) | Run discovery, assess a portfolio, plan waves, and pick a strategy per application against total cost of ownership | M |
| [dms-and-sct.md](dms-and-sct.md) | Choose a task type and endpoint pair, and tell homogeneous from heterogeneous migration | S |
| [application-migration-service.md](application-migration-service.md) | Replicate, test and cut over servers, and separate migration from disaster recovery | S |

## Which exam tasks this serves

On SAP-C02 these three units carry task 4.1, for portfolio assessment, the 7Rs
and total cost of ownership, and task 4.2, for selecting the transfer mechanism.
Tasks 4.3 and 4.4 finish that domain by asking which target platform to land on,
and the compute, container, database and storage categories teach those. On
SAA-C03 the footprint is smaller: task 2.2 covers improving legacy application
reliability, while tasks 3.3 and 4.3 both name homogeneous and heterogeneous
migration, and 4.3 asks about migrating database schemas and data
between engines. Note that **Migration Evaluator**, the cost assessment tool, is
on the SAA-C03 out-of-scope list.

## Reading order

Read `migration-hub-discovery-and-strategy.md` first, because the 7Rs and wave
planning are the frame the other two fit into. Then `dms-and-sct.md`, then
`application-migration-service.md`. An Associate-only candidate can compress
this to one pass: read the 7Rs section and the homogeneous against heterogeneous
rule in `dms-and-sct.md`, and skim the rest. The bulk-transfer tools that
migration questions also reach for live in the
[storage category](../01-storage/README.md).
