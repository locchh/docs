# AWS CloudFormation

**Where it sits on the exams.** **AWS CloudFormation** is the service that provisions and manages AWS resources from a declarative template, so that an environment is described once in a file and then created, updated or deleted as one unit. It answers the question of how infrastructure gets built repeatably, reviewed before it changes, and reproduced in another account or Region. It owns the SAA-C03 task 2.2 skill of determining automation strategies to ensure infrastructure integrity, and it owns SAP-C02 task 2.1, where infrastructure as code (IaC) is named with CloudFormation as the example, and SAP-C02 task 3.1, where prioritizing automation opportunities within a solution stack is the skill. The rule of thumb the exam rewards is that repeatability, consistency and reviewability point to a template, and the specific mechanism in the keyed answer follows from the word in the stem: preview a change means a change set, many accounts and Regions means StackSets, someone changed it by hand means drift detection, and this resource must survive means a deletion policy.

## What CloudFormation is and how a stack gets built

A CloudFormation template is a JSON or YAML text file that declares the resources you want. A **stack** is the set of resources created from one template, managed together: you create the stack, update it by submitting a changed template or changed parameter values, and delete it, which by default deletes every resource in it. That single unit of management is the whole point. Nothing tracks the relationship between a load balancer, its target group and its security group when they are created by hand in the console; a stack does, so it can tear them down in dependency order and rebuild them identically somewhere else.

Inside a template, each resource has a logical ID that you choose, a `Type` such as `AWS::EC2::Instance`, and a `Properties` block. When the stack is created, CloudFormation calls the underlying service APIs on your behalf and records the physical ID that comes back, for example the instance ID or the bucket name. The distinction between the logical ID, which is stable for the life of the resource in the stack, and the physical ID, which can change, drives several exam answers later in this unit. CloudFormation works out the dependency graph on its own from the references between resources, provisions independent branches in parallel, and only needs an explicit `DependsOn` attribute when an ordering requirement is not expressed by a reference.

CloudFormation is Regional. A stack lives in one Region, its name must be unique within that Region, and the default quota is 2,000 stacks per account, which is adjustable. There is no charge for CloudFormation itself when a template uses AWS resource types; you pay only for the resources the stack creates, at the same rate as if you had created them by hand. The one exception, covered later, is a per-operation charge for third-party extension types and custom Hooks.

Deployment normally runs from the **AWS Command Line Interface (AWS CLI)**, the command-line client for the AWS APIs, or from a pipeline that calls it. The `deploy` command is the usual entry point because it creates the stack if it does not exist and updates it if it does.

```bash
aws cloudformation deploy \
  --stack-name web-tier-prod \
  --template-file ./web-tier.yaml \
  --parameter-overrides Environment=prod InstanceType=m7i.large \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-execute-changeset
```

That `--capabilities` flag is an exam detail. **AWS Identity and Access Management (IAM)**, the service that decides which principal may perform which action on which resource, is powerful enough that CloudFormation refuses to create a stack containing IAM resources unless you acknowledge it. `CAPABILITY_IAM` covers IAM resources, `CAPABILITY_NAMED_IAM` is required when those resources carry custom names, and `CAPABILITY_AUTO_EXPAND` is required when a template contains macros and you deploy it directly rather than through a change set. Without the right acknowledgement the call fails with `InsufficientCapabilities`.

## Template anatomy and the intrinsic functions the exam tests

A template has ten possible top-level sections, and only `Resources` is required. `AWSTemplateFormatVersion` and `Description` are documentation. `Metadata` carries arbitrary data, including the `AWS::CloudFormation::Interface` key that groups parameters in the console. `Parameters` accepts input at deploy time. `Rules` validates parameters or combinations of parameters before the stack operation starts. `Mappings` is a static lookup table. A mapping is a fixed two-level lookup table resolved with `Fn::FindInMap`, and its classic use is a value that varies by Region, such as an AMI identifier:

```yaml
Mappings:
  RegionMap:
    us-east-1: {AMI: ami-0abcdef1234567890}
    eu-west-1: {AMI: ami-0fedcba9876543210}
Resources:
  Web:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
```

Mappings cannot use intrinsic functions or parameters in their keys, so anything dynamic belongs in a parameter or an SSM parameter lookup instead. `Conditions` decides whether a resource is created or a property is set. `Transform` names macros to run over the template. `Outputs` returns values from the finished stack.

Parameters are how one template serves several environments. A parameter needs a `Type`, which is the only required attribute, and the types are `String`, `Number`, `List<Number>`, `CommaDelimitedList`, the AWS-specific types such as `AWS::EC2::KeyPair::KeyName` and `AWS::EC2::Subnet::Id` that make the console offer a picker and validate the value, and the Systems Manager parameter types that read the current value out of Parameter Store, the configuration store inside **AWS Systems Manager**, the operations and management service, at deploy time. Constraints are `Default`, `AllowedValues`, `AllowedPattern`, `MinLength`, `MaxLength`, `MinValue` and `MaxValue`, with `ConstraintDescription` supplying a readable error. `NoEcho` masks a value as asterisks in the console, CLI and API, but AWS is explicit that it does not mask anything you put in the `Metadata` section or in `Outputs`, and recommends against putting secrets in parameters at all. The right answer for a password is a **dynamic reference**, the `{{resolve:...}}` syntax that pulls the value from **AWS Secrets Manager**, the managed secret store, or from Parameter Store at deploy time so the secret never appears in the template. A template may hold 60 dynamic references.

Intrinsic functions supply the values that are not known until runtime, and can be used in resource properties, outputs, metadata attributes and update policy attributes. Six of them carry most exam questions. `Ref` returns the value of a parameter, or for a resource its default identifier, usually the physical ID. `Fn::GetAtt` returns a named attribute of a resource, such as the ARN or the DNS name, and is the function you need whenever `Ref` returns the wrong thing. `Fn::Sub` substitutes variables into a string and is the readable replacement for nested `Fn::Join` calls. `Fn::FindInMap` reads a value out of `Mappings`, the classic use being a Region-to-AMI table. `Fn::ImportValue` reads an exported output from another stack. `Fn::If`, with `Fn::Equals`, `Fn::And`, `Fn::Or` and `Fn::Not`, evaluates a condition, and returning `AWS::NoValue` from an `Fn::If` removes the property entirely. Around those sit `Fn::Join`, `Fn::Split`, `Fn::Select`, `Fn::GetAZs` for the Availability Zones in a Region, `Fn::Base64` for user data, `Fn::Cidr` for carving subnet ranges out of a block, and `Fn::Transform` for invoking a macro inline.

**Pseudo parameters** are values CloudFormation supplies without being declared: `AWS::AccountId`, `AWS::Region`, `AWS::StackName`, `AWS::StackId`, `AWS::Partition`, `AWS::URLSuffix`, `AWS::NotificationARNs` and `AWS::NoValue`. Using them instead of hard-coded values is what makes a template portable across accounts and Regions.

```yaml
Conditions:
  IsProd: !Equals [!Ref Environment, prod]
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "reports-${Environment}-${AWS::AccountId}-${AWS::Region}"
      VersioningConfiguration:
        Status: !If [IsProd, Enabled, !Ref "AWS::NoValue"]
Outputs:
  BucketArn:
    Value: !GetAtt Bucket.Arn
    Export:
      Name: !Sub "${AWS::StackName}-bucket-arn"
```

A few functions, including `Fn::ForEach` for looping, `Fn::Length` and `Fn::ToJsonString`, exist only under the `AWS::LanguageExtensions` transform. They are worth knowing exist and are not worth exam study time.

Template quotas decide designs more often than they look like they should. A template may declare 500 resources, 200 parameters, 200 mappings with 200 attributes each, and 200 outputs. The template body passed directly in a `CreateStack`, `UpdateStack` or `ValidateTemplate` request is capped at 51,200 bytes, while a template read from a URL in **Amazon Simple Storage Service (Amazon S3)**, the object storage service, may be 1 MB. AWS names the same fix for all of these: split the template, usually into nested stacks.

## Change sets, update behaviors and rollback

Updating a stack in place is the operation that frightens people, and the **change set** is the feature that answers that fear. You submit a modified template or modified parameter values, and CloudFormation compares them with the deployed stack and produces a plan without touching anything. The plan lists which resources will be added, modified or deleted, with a before-and-after comparison of the properties and attributes that change, and it flags which modifications require replacement. You can create as many change sets as you like against the same stack to compare approaches, execute the one you want, and delete the rest; executing one removes all the others, because they no longer apply to the updated stack. Change set creation also runs pre-deployment validation for common failure causes, including property syntax errors, resource name conflicts and service quota limits. What it cannot do is guarantee success: AWS states plainly that "change sets don't guarantee that CloudFormation will successfully update a stack", because runtime conditions such as custom resource logic or service-specific constraints only appear during execution.

The reason the plan matters is that an update can do one of three things to each changed resource. An update with no interruption changes the resource while it keeps running and keeps its physical ID. An update with some interruption reconfigures the resource with a pause in service, the example AWS gives being certain property changes on an instance in **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service. A replacement recreates the resource with a new physical ID: CloudFormation creates the replacement first, repoints every dependent reference at it, and then deletes the original. Which behavior a given property produces is fixed by the resource type and documented per property in the resource reference, so `AvailabilityZone` on an EC2 instance and `Port` on an RDS DB instance both force replacement. Adding or removing a property that requires replacement triggers the update even when the effective value does not change. This is why a change set showing "Replacement: True" against a database is a stop signal, not a detail.

When something fails, the default is to roll the whole operation back, unless the operation uses express mode, a faster deployment mode that disables rollback by default. On create, `OnFailure` defaults to `ROLLBACK` and can be set to `DELETE` or `DO_NOTHING`; on update, failure rolls the stack back to its last known stable state. Choosing the preserve successfully provisioned resources option, which is `--disable-rollback` or `OnFailure DO_NOTHING` on the CLI, changes that: the stack stops at `CREATE_FAILED` or `UPDATE_FAILED` with the successful resources intact, and you then fix the cause and issue a retry, an update, or an explicit roll back. That is the fastest path through a long stack that failed on resource number forty, and it is the answer when a stem complains about waiting for a full rebuild after every failed attempt. Note that a `rollback-stack` call deletes the stack outright if it has no last known stable state.

Two failure states have their own answers. A stack whose creation failed and rolled back sits in `ROLLBACK_COMPLETE` and must be deleted and recreated rather than updated. A stack whose update rollback could not finish sits in `UPDATE_ROLLBACK_FAILED`, usually because a resource the rollback wanted to restore was deleted outside CloudFormation. Such a stack cannot be updated, but it can be rolled back: you fix the underlying cause and call continue update rollback, optionally naming logical IDs in `--resources-to-skip` so the rollback can finish. Skipping leaves those resources inconsistent with the template, and you must reconcile them before the next update or the stack becomes unrecoverable.

Rollback triggers extend rollback from "the API call failed" to "the application got worse". You attach up to five alarms from **Amazon CloudWatch**, the AWS monitoring and observability service, either `AWS::CloudWatch::Alarm` or `AWS::CloudWatch::CompositeAlarm`, plus a monitoring time from 0 to 180 minutes. CloudFormation watches those alarms during the operation and for the monitoring period after every resource is deployed, and rolls the entire operation back if any of them enters `ALARM`. By default `INSUFFICIENT_DATA` does not trigger a rollback; you get that behavior by configuring the alarm to treat missing data as breaching. A missing alarm fails the operation. For an update, if the monitoring period expires with no breach, CloudFormation then disposes of the old resources, which is what makes the monitoring window a real bake time rather than a formality.

## Protecting resources: stack policies, service roles and deletion policies

Four separate controls guard a stack, and the exam tests whether you can tell them apart. A **stack policy** protects resources during updates. A service role controls what CloudFormation itself may do. **Termination protection** stops the stack being deleted. The `DeletionPolicy` and `UpdateReplacePolicy` attributes decide what happens to a resource when CloudFormation would otherwise destroy it.

A stack policy is a JSON document set on a stack, not on an identity. When a stack is created no policy is set and every update action is allowed, but once you set one "all of the resources in the stack are protected by default", so a usable policy pairs a broad `Allow` with a narrow `Deny`. The elements are `Effect`, `Action`, `Principal`, `Resource` and `Condition`. `Principal` is required and accepts only `*`, which is the tell that a stack policy is not an access control: AWS says it "doesn't provide access controls like an AWS Identity and Access Management (IAM) policy" and to "use a stack policy only as a fail-safe mechanism". The actions are `Update:Modify`, `Update:Replace`, `Update:Delete` and `Update:*`. Resources are named by logical ID as `LogicalResourceId/MyDatabase`, with wildcards allowed, and a `Condition` on `ResourceType` protects every resource of a type. A `Deny` always overrides an `Allow`, so protection must be written as an explicit `Deny`; AWS specifically warns that `NotResource` with `Effect: Allow` does not reliably protect the excluded resource. There is one policy per stack, it applies to every user, it cannot be deleted once set, and you update a protected resource by passing a temporary override policy for that one operation with `--stack-policy-during-update-body`.

```json
{
  "Statement": [
    { "Effect": "Deny", "Action": "Update:*", "Principal": "*",
      "Resource": "LogicalResourceId/ProductionDatabase" },
    { "Effect": "Allow", "Action": "Update:*", "Principal": "*", "Resource": "*" }
  ]
}
```

A service role is the opposite control: it constrains CloudFormation rather than the template. By default "CloudFormation uses a temporary session that it generates from your user credentials", which means a stack can do anything its operator can do. Attach a service role, an IAM role trusted by `cloudformation.amazonaws.com`, and CloudFormation uses that role's credentials instead, so an administrator can restrict a stack to Amazon EC2 actions even though the administrator has more. Two facts follow. Passing the role requires the `iam:PassRole` permission, and once a service role is attached to a stack it cannot be removed, and other users with permission to operate on that stack can use it whether or not they hold `iam:PassRole`. An over-broad service role is therefore a privilege escalation path, which is why the role should grant least privilege.

Termination protection is a flag on the stack, disabled by default, that makes `DeleteStack` fail outright. It is set on the root stack and passes to every nested stack below it, and it cannot be set directly on a nested stack. AWS draws the line explicitly: "termination protection applies only to attempts to delete stacks, while disabling rollback applies to auto rollback when stack creation fails." It also does not stop an update from deleting a nested stack that the update removes.

The last control works at resource level. `DeletionPolicy` says what happens when the stack is deleted, or when the resource is removed from the template during an update. `Delete` is the default and destroys the resource. `Retain` keeps it, removed from CloudFormation's scope but still incurring charges. `RetainExceptOnCreate` behaves like `Retain` for every operation except the one that created the resource, so a rolled back creation deletes the new empty resource while a later deletion keeps the populated one. `Snapshot` takes a snapshot first, and is supported on a short list of resources that includes volumes in **Amazon Elastic Block Store (Amazon EBS)**, the network-attached block storage service, clusters and instances in **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, and the cache and data warehouse cluster types that support snapshots. The default is `Snapshot`, not `Delete`, for `AWS::RDS::DBCluster` and for `AWS::RDS::DBInstance` resources that do not specify `DBClusterIdentifier`.

`UpdateReplacePolicy` takes the same three values but fires only when an update replaces a resource. It is easy to get this wrong in both directions: `DeletionPolicy` does not apply to a replacement, and `UpdateReplacePolicy` does not apply to a stack deletion. A database that must never be lost needs both, usually `DeletionPolicy: Retain` and `UpdateReplacePolicy: Snapshot`. If you set `Snapshot` on a resource type that does not support snapshots, CloudFormation silently reverts to `Delete`.

## Nested stacks compared with cross-stack references

Templates hit the 500-resource ceiling, and teams want to reuse a pattern rather than paste it. There are two ways to compose templates, and the exam separates them by lifecycle.

**Nested stacks** embed one template inside another. The parent declares an `AWS::CloudFormation::Stack` resource whose `TemplateURL` points at the child template in Amazon S3, passes values down through `Parameters`, and reads values back up with `Fn::GetAtt` on `NestedStack.Outputs.Name`. The stack at the top of the hierarchy is the root stack; each nested stack also has an immediate parent. The `aws cloudformation package` command uploads local child templates to a bucket and rewrites every `TemplateURL` for you, which is how nested stacks are used in practice. Operationally the hierarchy behaves as one thing: you update the root, not the child, and an update of the root initiates an update of every nested stack so CloudFormation can tell which ones changed, though only changed resources are touched. A nested stack stuck in `UPDATE_ROLLBACK_IN_PROGRESS` stalls the root until it finishes. The relevant quota is that a nested stack hierarchy can create, update or delete at most 2,500 resources in a single operation, even though the hierarchy as a whole may hold more.

**Cross-stack references** connect stacks that have separate lifecycles. The producing stack adds an `Export` with a name to an entry in its `Outputs` section; the consuming stack reads it with `Fn::ImportValue`. Four restrictions decide questions. Export names must be unique per account within a Region. Export and `Fn::ImportValue` work only within the same account and Region. Neither the export name nor the `ImportValue` argument may use a `Ref` or `Fn::GetAtt` that depends on a resource, so the export name has to be a literal or a pseudo parameter substitution. And, the one that surprises people in production, "after another stack imports an output value, you can't delete the stack that is exporting the output value or modify the exported output value" until every import is removed. That is not a bug. It is deliberate referential integrity: the network stack cannot delete the subnet that twelve application stacks are sitting in. `aws cloudformation list-imports --export-name <name>` tells you who is holding the lock.

A recent addition, `Fn::GetStackOutput`, reads another stack's output directly without requiring an export, and it does work across Regions with a `Region` parameter and across accounts with a `RoleArn` naming a role that holds `cloudformation:DescribeStacks` on the referenced stack and is assumable by the consuming stack's execution role. It does not cross partitions. The trade is that it creates a weak reference: CloudFormation does not block deletion of the referenced stack, and a later operation that re-resolves a reference to something that no longer exists simply fails. Treat it as current practice rather than as exam vocabulary. Both exam guides predate it, and the framing they test is that an export is same-account and same-Region, so the long-standing keyed answer for passing a value into another Region or account is a template parameter or a Parameter Store lookup. Read this table when a scenario asks how one stack should consume another's values.

| Mechanism | Scope | Lifecycle coupling | Choose it when |
|---|---|---|---|
| Nested stacks | One hierarchy, one account and Region | Deployed, updated and deleted as one unit from the root | The pieces are parts of one application and always ship together, or the template is too large for one file |
| `Export` with `Fn::ImportValue` | Same account, same Region | Strong: the exporting stack cannot be deleted or its export changed while imported | Long-lived shared infrastructure such as a VPC, subnets or a shared security group, consumed by independently deployed stacks |
| `Fn::GetStackOutput` | Cross-account and cross-Region, but not cross-partition | Weak: nothing is blocked and nothing is notified | The value lives in another account or Region, or you do not want to manage exports. Recent, so treat it as practice rather than exam vocabulary |

AWS states the choice in one sentence: "If you want to isolate information sharing to within a nested stack group, we suggest that you use nested stacks. To share information with other stacks (not just within the group of nested stacks), export values."

## StackSets across accounts and Regions

**StackSets** deploys one template to many accounts and many Regions in a single operation. The account you create the stack set in is the administrator account; the accounts it deploys into are target accounts; and a **stack instance** is the reference to one stack in one target account in one Region. A stack set is itself a Regional resource, so it is visible only in the Region where it was created, though the stacks it creates can be anywhere. Updating the stack set pushes the template to every associated stack instance; you cannot update the template for only some of them, though you can override parameter values per stack instance.

The permission model is the part exam questions turn on. With self-managed permissions you create the trust yourself: an IAM role named `AWSCloudFormationStackSetAdministrationRole` in the administrator account, trusted by `cloudformation.amazonaws.com` and permitted to assume the execution role, and a role named `AWSCloudFormationStackSetExecutionRole` in every target account, trusting the administrator account and carrying the permissions the template needs. The execution role name must be identical in every target account, and if it carries that default name StackSets uses it automatically; a custom name must be supplied on every operation. Self-managed permissions work with any account where you can create a role, which is the reason to choose them: the targets do not have to be in an organization at all.

With service-managed permissions, **AWS Organizations**, the multi-account governance service, supplies the trust. The prerequisites are that the organization has all features enabled, not just consolidated billing, and that trusted access for StackSets is activated. CloudFormation then creates the roles for you: the service-linked role `AWSServiceRoleForCloudFormationStackSetsOrgAdmin` in the management account, and in each target account `AWSServiceRoleForCloudFormationStackSetsOrgMember` together with a service role named `stacksets-exec-*`. You then target organizational units rather than a list of account IDs, and either the management account or a registered delegated administrator can create and manage the stack sets. The limitation to remember is that a service-managed stack set cannot be created or updated from a template that contains macros, which includes hosted transforms.

Automatic deployment is the feature service-managed permissions exist for. Enable it and a new account added to a target organizational unit gets the stack created in it without anyone doing anything, in every target Region. Moving an account from one targeted unit to another runs a delete for the old stack set and queues a create for the new one. When an account leaves a target unit you choose the behavior: delete the stacks, or retain them, in which case the resources stay in their current state but leave the stack set's management. Automatic deployment is a stack set level setting that cannot be turned on for some units and off for others, and it ignores account-level targeting filters, so a stack set that targets specific accounts inside an organizational unit will still deploy to newly added accounts unless automatic deployment is off. This is the mechanism behind "every new account must automatically receive our baseline logging and guardrail stack".

Operation preferences control blast radius. Maximum concurrent accounts caps how many target accounts an operation runs in at once, as a number or a percentage that rounds down. Failure tolerance sets how many stack failures are allowed per Region before CloudFormation stops the operation; exceeding it in one Region cancels the remaining Regions. Region concurrency is sequential by default, following the deployment order you specify, or parallel. The quotas that bite at scale are 1,000 stack sets per administrator account, 100,000 stack instances per stack set, and 10,000 stack instance operations running at the same time per Region per administrator account.

## Drift detection, resource import and the IaC generator

Infrastructure integrity fails in two directions: resources under CloudFormation management get changed by hand, and resources that were never under management accumulate. CloudFormation has a tool for each.

**Drift detection** compares the actual configuration of each resource with the expected configuration from the stack template and the parameter values that were supplied. A resource is `IN_SYNC`, `MODIFIED`, `DELETED`, or `NOT_CHECKED`, and a stack is considered drifted if one or more of its resources have drifted. For a modified resource CloudFormation reports each differing property with a difference type of `ADD`, `REMOVE` or `NOT_EQUAL` plus the expected and actual values. Stack-level tags are checked too.

What drift detection cannot see matters more than what it can. Resource types that do not support drift detection are simply reported `NOT_CHECKED`, and no count of drifted resources will ever include them. AWS "only determines drift for property values that are explicitly set, either through the stack template or by specifying template parameters", so a property you left at its default is invisible to drift even after somebody changes it; to have it tracked you must set it in the template, even to the default value. Detecting drift on a stack does not detect drift on its nested stacks, which must be checked individually. The `KMSKeyId` property of any resource is never checked, because a key in **AWS Key Management Service (AWS KMS)**, the managed key service, can be named by several aliases. Properties that cannot be mapped back to a template value, such as the source code of a function in **AWS Lambda**, the event-driven function service, and properties a service never returns, such as an IAM login profile password, are excluded by design. Cross-stack attachment relationships, for example a security group rule declared in a different stack from its security group, can produce inaccurate results, and equal-but-not-identical values such as 1024 MB against 1 GB produce false positives. Finally, drift detection is an operation you run, not a monitor: it is point in time, it can only run on a stack in `CREATE_COMPLETE`, `UPDATE_COMPLETE`, `UPDATE_ROLLBACK_COMPLETE` or `UPDATE_ROLLBACK_FAILED`, the caller needs read permission on every resource type in the stack, and a scenario that asks for continuous detection of configuration change wants **AWS Config**, the resource configuration and compliance service, with drift detection scheduled alongside it.

Drift detection on a stack set runs the same check against the stack behind each stack instance and rolls the result up, so a stack set is drifted if any instance is. A change made through CloudFormation to one member stack is not drift, because the stack still matches its own recorded template.

The second direction is adoption. **Resource import** brings an existing resource under stack management without deleting and recreating it: you add the resource to the template with a `DeletionPolicy` and supply its identifier, and CloudFormation adopts it rather than creating it. The same machinery is what lets you move resources between stacks, nest an existing stack inside another, or use stack refactoring to split and merge stacks while preserving data. The **IaC generator** automates the hard part. It runs a Region-wide scan of the resources in the account that CloudFormation does not already manage, keeps that scan for 30 days, lets you pick resources and their discovered related resources, and writes a JSON or YAML template you can then import as a stack. A scan processes up to 100,000 resources and a single generated template can model up to 500 of them, and it only covers resource types supported by the Cloud Control API, the uniform create, read, update, delete and list interface over registry resource types, in that Region. That pipeline, scan then generate then import, is the keyed answer to "bring a manually built production environment under source control without an outage".

## Extending CloudFormation: custom resources, macros, Hooks and the registry

When a template needs something CloudFormation cannot express, four extension points cover it, and they are easy to confuse.

A **custom resource** runs your own provisioning logic as part of a stack operation. You declare it as `Custom::MyThing` or `AWS::CloudFormation::CustomResource` with one required property, `ServiceToken`, holding the ARN of a Lambda function or a topic in **Amazon Simple Notification Service (Amazon SNS)**, the publish-and-subscribe service, in the same Region as the stack. On create, update and delete, CloudFormation sends a request containing the `RequestType`, the `ResourceProperties`, and a `ResponseURL` that is a pre-signed S3 URL, and then waits. The provider does the work and uploads a JSON response to that URL with a `Status` of `SUCCESS` or `FAILED`, a `PhysicalResourceId`, and an optional `Data` object whose name-value pairs the template reads with `Fn::GetAtt`. The protocol detail that decides exam questions and real incidents is what happens when nothing is uploaded: "if a `FAILED` response or no response is returned, the operation fails", and the default timeout is 3600 seconds, so a function that throws an exception before writing its response leaves the stack waiting an hour. Set the `ServiceTimeout` property to something realistic, and wrap the handler so it reports failure rather than crashing. A function in a private subnet must still be able to reach Amazon S3 to post the response.

**Macros** transform the template itself rather than provisioning anything. You name them in the `Transform` section and CloudFormation runs them in order over the template before deploying it. The hosted transforms are `AWS::Include`, which splices in a stored snippet, and `AWS::Serverless`, which expands AWS Serverless Application Model syntax into ordinary CloudFormation. Custom macros are backed by a Lambda function, whose owner is billed for its execution. Because a macro can rewrite anything, deploying a template with one directly, rather than reviewing the processed result in a change set first, requires the `CAPABILITY_AUTO_EXPAND` acknowledgement, and service-managed stack sets do not support templates with macros at all.

**CloudFormation Hooks** are preventive policy, not provisioning. A Hook inspects the configuration of resources, stacks or change sets before they are provisioned and either fails the operation or emits a warning and lets it continue, and it covers Cloud Control API calls as well as CloudFormation. You can implement one from the **AWS Control Tower**, the multi-account landing zone service, proactive control catalog without writing code, from AWS CloudFormation Guard policy-as-code rules, from a Lambda function, or as a custom extension built with the CloudFormation CLI. This is the difference between preventive and detective control that Professional questions lean on: a Config rule reports an unencrypted volume after it exists, a Hook stops the stack operation that would create it. The quota is 100 Hooks per account per Region and 100 per resource.

The **CloudFormation registry** is where extensions live. It holds resource types, **modules** and Hooks, published by AWS, by third parties, or privately by you, and you activate a public third-party extension in your account before templates can use it. Registry-based resource types support create, read, update, delete and list operations and support drift detection, which custom resources do not, and they need no Lambda function or SNS topic of their own. Modules package a group of resource configurations behind one logical entry in a template; they are resolved when the template is processed, so the resources they expand into count against the 500-resource and template-size quotas exactly as if you had typed them, and there is no extra charge for using one. The registry is also where the only CloudFormation charge appears. AWS resource types are free and you pay only for what the stack creates; third-party and private registry resource types and custom Hooks are billed per handler operation, with a duration component beyond a free threshold per operation and a shared monthly free tier of operations.

## Git sync and choosing a provisioning tool

Templates belong in version control, and **Git sync** removes the pipeline you would otherwise write to get them from there into an account. You link a repository through **AWS CodeConnections**, the managed connection to external source providers, and CloudFormation then watches two files: the template that defines the stack, and a stack deployment file holding the parameters and configuration for one stack. Commit a change to either and CloudFormation updates the stack. Enable the pull request feature and it comments on the pull request describing what the change would do, which turns a change set review into a code review. Git sync supports GitHub, GitHub Enterprise, GitLab, GitLab self-managed and Bitbucket, offers a status dashboard, and is available in a subset of Regions rather than all of them. When a stem asks for a deployment process where the repository is the source of truth and there is no pipeline to maintain, this is the low-overhead answer; when it asks for build, test and approval stages, the answer is a pipeline, covered in [developer tools and CI/CD](developer-tools-and-cicd.md).

Four tools come up whenever infrastructure as code is discussed, and the exam treats them very differently. Read the last column first, because it decides where your study time goes.

| Tool | What it is | How it reaches AWS | Exam status |
|---|---|---|---|
| AWS CloudFormation | AWS-native declarative service; JSON or YAML templates, state held by the service in the stack | Calls service APIs directly and records logical-to-physical mappings | In scope for SAA-C03 and named in SAP-C02 task 2.1. This is the examinable one |
| **AWS Cloud Development Kit (AWS CDK)** | Framework for defining infrastructure in TypeScript, Python, Java, Go or C# | Synthesizes a CloudFormation template and deploys it as a stack | On the SAA-C03 out-of-scope service list. Do not spend study time on it. It appears here only because a scenario may mention it, and the correct reading is that it becomes CloudFormation |
| Terraform | Third-party open-source tool with its own configuration language and provider model, spanning many clouds | Calls provider APIs and keeps its own state file, which you must store and lock yourself | Third-party context, not exam material. AWS exams do not test it |
| Pulumi | Third-party tool that defines infrastructure in general-purpose programming languages | Calls provider APIs against state held in its own backend | Third-party context, not exam material |

The distinction worth carrying into the exam is state. CloudFormation keeps the mapping between template and reality inside the stack, which is what makes change sets, drift detection, rollback and stack policies possible without a file you have to store, lock and back up. CDK is not a competing model at all; it is a program that emits a template, so every fact in this unit applies to a CDK deployment unchanged.

Within AWS, three provisioning services are in scope, and they sit on a ladder of abstraction. CloudFormation gives you every resource and every knob. **AWS Elastic Beanstalk**, the managed application platform that provisions and operates the environment for a conventional web application from your uploaded code, sits above it and is the answer when a team wants a deployed application without designing the stack; it is taught in [AWS Elastic Beanstalk](../02-compute/elastic-beanstalk.md). **AWS Service Catalog**, the service that publishes approved CloudFormation templates as products in portfolios that end users can launch under a constrained role, sits beside it and is the answer when the requirement is that non-specialists provision only approved architectures with the permissions the launch constraint grants rather than their own; it is taught in [AWS Service Catalog](service-catalog.md). For one-off or scripted calls rather than managed infrastructure, the AWS CLI and the SDKs remain the right tools, and they are taught in [the AWS API, CLI and SDKs](aws-api-cli-and-sdks.md).

## Professional depth

Prioritizing what to automate is a Professional skill in its own right, and the order is not arbitrary. Automate first what is repeated across the most accounts and Regions, because the saving multiplies and the inconsistency you remove is the kind that causes incidents: account baselines, network patterns, guardrail roles. Automate next what has the largest blast radius when it is wrong, because a template plus a change set turns an irreversible console click into a reviewed diff. Automate last, or never, the one-off and the genuinely exploratory, where a template costs more to write than the task costs to repeat. The tie-breaker is drift: anything people keep changing by hand is either a candidate for automation or a sign the template is wrong, and drift detection is how you find out which.

At organization scale the unit of deployment stops being a stack and becomes a stack set. A platform team registers a security or shared-services account as the delegated administrator for StackSets, creates service-managed stack sets that target organizational units rather than account lists, and enables automatic deployment so that a newly vended account receives the baseline before anyone logs into it. That baseline is usually several small stack sets rather than one large one, because a stack set update is all-or-nothing across its instances and a small blast radius is the only way to roll a change out safely. AWS Control Tower's Account Factory and a service-managed stack set are complementary rather than alternative: Control Tower vends and governs the account, and the stack set puts your own resources in it. The management account should not be the administrator account for day-to-day work, both because organization policies do not constrain it and because a delegated administrator keeps the blast radius of a mistake inside a member account.

Blast radius is configured, not hoped for. Failure tolerance is evaluated per Region, so setting it low means the operation stops in the first Region that goes wrong and never reaches the rest. Maximum concurrent accounts and sequential Region concurrency with an explicit deployment order let you stage a rollout through a test organizational unit, then one Region, then the world. Stack sets themselves are Regional resources, which makes the administrator Region a real dependency in a disaster recovery plan: if you manage 90 accounts from stack sets in one Region, losing that Region does not break the deployed stacks but does stop you deploying.

Quotas shape template architecture long before they cause errors. Five hundred resources per stack forces a real estate into layers: network, shared services, per-application. A nested stack hierarchy can hold more than 2,500 resources but cannot create, update or delete more than 2,500 in a single operation, so a monolith that grew by nesting eventually cannot be updated at all. Ten thousand concurrent stack instance operations per Region per administrator account is the ceiling a large parallel rollout hits.

The failure mode that costs the most time at scale is the export web. Every `Fn::ImportValue` is a lock on the exporting stack: you cannot change or remove that export, or delete its stack, until every importer stops using it. On an estate with a dozen application stacks importing from one network stack, changing a subnet export becomes a coordinated multi-team release. The mitigations are to export only values that are genuinely permanent, to prefer passing values in as parameters resolved from Parameter Store where the coupling should be loose, and to use `Fn::GetStackOutput` where a weak reference is acceptable and the values cross an account or Region boundary. The related recovery problem is the stack in `UPDATE_ROLLBACK_FAILED` after someone deleted a resource by hand during an incident, which needs continue update rollback with the right set of skipped logical IDs, followed by an import or a template correction to make the stack honest again.

Security at this scale is layered the way IAM is. A service role per environment means the production stack can only touch production resource types, whatever the operator's own permissions are, and the fact that a service role cannot be removed after it is attached makes the initial choice a design decision. Hooks, built from Control Tower proactive controls or Guard rules, refuse non-compliant resources at provisioning time, which is cheaper than detecting them in Config afterwards and cheaper still than remediating them in production. Stack policies stay as the last fail-safe over data stores, paired with `DeletionPolicy: Retain` and `UpdateReplacePolicy: Snapshot` so that neither an operator error nor a property change that forces replacement can destroy the data.

> **Professional depth.** A Professional question often extends an Associate change set scenario across accounts. The Associate answer is "create a change set and review it before executing". The Professional answer keeps that, and adds a service-managed stack set from a delegated administrator so the change reaches every account, a low failure tolerance with sequential Region concurrency so a bad change stops after one Region, and Hooks so the non-compliant resource never gets as far as a change set. Rollback triggers do not apply here: they are a parameter of create-stack, update-stack and create-change-set, not of a stack set operation, so a stack set relies on failure tolerance and concurrency for its blast radius control.

## Worked scenario

A financial services company runs 90 accounts in one organization with all features enabled. A platform team in a delegated administrator account owns the baseline: a logging configuration, a set of guardrail roles, and a VPC pattern that every workload account must have, in three Regions. Each business unit deploys its own applications. One production application has an RDS database whose loss would be a reportable event. A newly acquired subsidiary has a manually built environment in a separate account that must come under source control without downtime.

The baseline goes into three small service-managed stack sets targeting the workload organizational units, with automatic deployment enabled so that every new account created by Account Factory receives them, and with account removal set to retain stacks so that an account leaving an organizational unit does not have its logging deleted underneath an investigation. Operation preferences set maximum concurrent accounts to a low percentage, failure tolerance to a small number per Region, and sequential Region concurrency with a test Region first. A Hook built from a Guard rule refuses any resource that would create an unencrypted volume or a public bucket, so non-compliant templates fail before provisioning in every account.

The application stacks are separate. The network stack exports its VPC and subnet IDs; the application stacks import them, which is exactly the coupling the company wants, because it makes deleting a shared subnet impossible while anything is using it. Inside the application, the database sits in its own stack with `DeletionPolicy: Retain` and `UpdateReplacePolicy: Snapshot`, a stack policy denying `Update:Replace` and `Update:Delete` on that logical ID, and termination protection on the stack. Deployments run through Git sync from the application repository, so a pull request shows what will change, and the production stack carries a service role limited to the resource types that application uses. Rollback triggers watch the application's error-rate alarm for 15 minutes after each update.

For the acquired account, the team runs an IaC generator scan, selects the running resources and their related resources, generates a template, and imports them into a new stack. Nothing is recreated, so there is no downtime. A drift detection run immediately afterwards establishes the baseline, and the differences it reports are reconciled by editing the template rather than by touching the resources.

When the exam asks about this scenario, the keyed answer is a service-managed stack set with automatic deployment for the organization-wide baseline, cross-stack exports for the shared network, `DeletionPolicy` and `UpdateReplacePolicy` plus a stack policy for the database, change sets or Git sync pull request comments as the review gate, and the IaC generator followed by resource import to adopt the acquired environment.

## Exam lens

- "Provision the same infrastructure in a new Region or account with no manual steps" maps to deploying the same CloudFormation template; copying resources by hand or using an AMI is the distractor.
- "Review exactly what an update will change before it happens" maps to a change set; drift detection answers a different question, about changes that already happened outside CloudFormation.
- "Find out whether anyone changed the resources outside CloudFormation" maps to drift detection; a change set will not tell you.
- "Continuously detect and remediate configuration changes" maps to AWS Config rules, not drift detection, which is an operation you run at a point in time.
- "Stop non-compliant resources from ever being provisioned" maps to CloudFormation Hooks; a Config rule is the detective distractor that fires after the resource exists.
- "Deploy a baseline to every account in the organization, including accounts created later" maps to a service-managed StackSet with automatic deployment enabled; self-managed permissions are the distractor because they require you to create roles in each new account.
- "Deploy to accounts that are not part of our organization" maps to self-managed StackSet permissions with `AWSCloudFormationStackSetAdministrationRole` and `AWSCloudFormationStackSetExecutionRole`.
- "The database must survive deletion of the stack" maps to `DeletionPolicy: Retain`; termination protection stops the stack being deleted but does nothing when the resource is removed from the template.
- "Keep a copy of the data when an update replaces the database" maps to `UpdateReplacePolicy: Snapshot`; `DeletionPolicy` does not apply to replacement.
- "Prevent an update from accidentally replacing the production database" maps to a stack policy denying `Update:Replace` on that logical ID; an IAM policy controls who may call the update, not what the update may do to one resource.
- "CloudFormation must not be able to do more than this application needs, even for an administrator" maps to a service role on the stack.
- "Roll the deployment back automatically if error rates rise after it completes" maps to rollback triggers with CloudWatch alarms and a monitoring period, not to a change set.
- "Do not delete the 40 resources that succeeded when resource 41 fails" maps to the preserve successfully provisioned resources option, then retry.
- "Share a VPC ID from a network stack to application stacks in the same account and Region" maps to an `Export` output plus `Fn::ImportValue`; the exporting stack then cannot be deleted or the export changed while any import exists.
- "Reference an output from a stack in another account or Region" rules out `Fn::ImportValue`, because exports do not cross an account or Region boundary; the exam-era answer is a template parameter or a Parameter Store lookup, and `Fn::GetStackOutput` is the current mechanism if an option offers it.
- "The template is too large, or the same pattern is repeated in many templates" maps to nested stacks, or to a registry module for a reusable block.
- "Provision something CloudFormation has no resource type for" maps to a custom resource backed by Lambda; if the stack hangs for an hour, the function failed without posting a response to the pre-signed URL.
- "Bring manually created production resources under CloudFormation without downtime" maps to the IaC generator scan followed by a resource import; deleting and recreating from a new template is the distractor that breaks the no-downtime requirement.
- "Let non-specialist teams launch only approved architectures with permissions they do not hold" maps to AWS Service Catalog products with a launch constraint, not to giving them CloudFormation access.

A related primitive is `AWS::CloudFormation::WaitCondition`, which pauses a stack until a configured number of success signals arrive at a pre-signed URL or until a timeout expires. It predates custom resources and Lambda-backed logic, and the modern answer to "wait until the application is actually up" is usually a `CreationPolicy` with `cfn-signal` on an Auto Scaling group or a custom resource. Recognize it when a question names it, but do not reach for it first.

## Knowledge check

### 1. Seeing what an update will do (Associate)

A company manages a production web tier with a CloudFormation stack. An engineer has modified the template to change several resource properties. Before applying the change, the operations team must see which resources will be modified, which will be deleted, and which will be recreated with new identifiers, without any resource being touched during the review.

Which solution will meet these requirements?

- **A)** Run drift detection on the stack and review the resource drift results.
- **B)** Create a change set from the modified template, review the listed changes, and execute it once approved.
- **C)** Update the stack with the preserve successfully provisioned resources option and review the stack events.
- **D)** Deploy the modified template to a copy of the stack in another Region and compare the two stacks.

<details><summary>Answer</summary>

**Answer: B.** A change set compares the submitted template with the deployed stack and produces a plan showing additions, modifications and deletions with a before-and-after view of the affected properties, and it flags which changes require replacement. Nothing changes until you execute the change set. A reports differences between the stack and resources as they exist now, which is about unmanaged changes already made, not about a proposed update. C applies the update and only preserves resources that already succeeded when a later one fails, so resources are modified during the review. D creates real resources in a second Region, which costs money, takes time, and still does not tell you what the update would do to the existing stack.

*Where this is covered: Change sets, update behaviors and rollback.*

</details>

### 2. Keeping data when the stack goes away (Associate)

A team deploys an analytics environment with CloudFormation. The stack includes an Amazon S3 bucket holding processed results that must remain available after the environment is torn down at the end of each quarter. The rest of the stack's resources should be deleted normally.

Which solution will meet these requirements?

- **A)** Enable termination protection on the stack.
- **B)** Add `UpdateReplacePolicy: Retain` to the bucket resource.
- **C)** Add `DeletionPolicy: Retain` to the bucket resource.
- **D)** Add a stack policy that denies `Update:Delete` on the bucket's logical ID.

<details><summary>Answer</summary>

**Answer: C.** `DeletionPolicy: Retain` tells CloudFormation to leave the resource in place when the stack is deleted, removing it from the stack's scope while everything else is deleted as usual. A prevents the stack from being deleted at all, which contradicts the requirement to tear the environment down. B applies only when an update replaces a resource, not when the stack is deleted. D is a stack policy, which AWS documents as applying only during stack updates, so it has no effect on a delete operation.

*Where this is covered: Protecting resources: stack policies, service roles and deletion policies.*

</details>

### 3. Guarding a production database through updates (Associate)

A production CloudFormation stack contains an Amazon RDS DB instance alongside application resources that are updated weekly. The company requires that no stack update can ever replace or delete the DB instance without a deliberate, separate action, and that if a replacement is ever performed on purpose, the data from the old instance is still recoverable.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable termination protection on the stack.
- **B)** Set a stack policy with an explicit `Deny` for `Update:Replace` and `Update:Delete` on the DB instance's logical ID, with an `Allow` for all update actions on all other resources.
- **C)** Attach an IAM policy to the deployment role that denies `rds:DeleteDBInstance`.
- **D)** Add `UpdateReplacePolicy: Snapshot` to the DB instance resource.
- **E)** Add a `NotResource` statement with `Effect: Allow` that excludes the DB instance's logical ID.

<details><summary>Answer</summary>

**Answer: B and D.** The explicit `Deny` in the stack policy is the documented way to protect a resource during updates, because a `Deny` always overrides an `Allow`, and updating that resource then requires passing a temporary override policy for that one operation. `UpdateReplacePolicy: Snapshot` makes CloudFormation take a snapshot before deleting the old instance when a replacement does happen, which is exactly the recoverability requirement. A only blocks deletion of the whole stack and does nothing during an update. C misses on two counts: an IAM policy acts on a resource type rather than one logical ID, so it would block every database in the account, and by default CloudFormation acts with a session generated from the caller's own credentials, so such a deny would bite the deployment too. It also does nothing for the recoverability requirement. E is the pattern AWS explicitly warns against: `NotResource` with `Effect: Allow` does not reliably protect the excluded resource, because the resource type is still implicitly allowed.

*Where this is covered: Protecting resources: stack policies, service roles and deletion policies.*

</details>

### 4. A baseline for accounts that do not exist yet (Associate)

A company uses AWS Organizations with all features enabled. Every account in the Workloads organizational unit must have the same logging configuration and IAM guardrail roles in three Regions. New accounts are created every month and must receive the same configuration without anyone running a deployment.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a CloudFormation stack in each account and add a monthly calendar reminder to repeat it for new accounts.
- **B)** Create a StackSet with self-managed permissions and add each new account as a target after it is created.
- **C)** Create a CloudFormation template and distribute it to account owners with instructions to deploy it.
- **D)** Create a StackSet with service-managed permissions that targets the Workloads organizational unit in the three Regions, and enable automatic deployment.

<details><summary>Answer</summary>

**Answer: D.** Service-managed permissions let a stack set target an organizational unit rather than a list of accounts, and automatic deployment creates the stack in any account that is added to that unit, in every target Region, with no operator action. A and C both depend on a human repeating work for every new account, which is the overhead the requirement removes. B is closer but still requires someone to add each new account as a target and to create the execution role in it, because self-managed permissions do not follow organization membership.

*Where this is covered: StackSets across accounts and Regions.*

</details>

### 5. Deploying to accounts outside the organization (Professional)

A managed service provider operates infrastructure in 30 AWS accounts that belong to its customers. None of those accounts is a member of the provider's own AWS organization. The provider must deploy and maintain a standard monitoring stack in all 30 accounts across two Regions from a single administrator account.

Which solution will meet these requirements?

- **A)** Create a StackSet with self-managed permissions, create the `AWSCloudFormationStackSetAdministrationRole` in the administrator account, and have each customer create an `AWSCloudFormationStackSetExecutionRole` that trusts the administrator account.
- **B)** Create a StackSet with service-managed permissions and register the administrator account as a delegated administrator.
- **C)** Invite all 30 customer accounts into the provider's organization and use a service-managed StackSet with automatic deployment.
- **D)** Create an IAM user in each customer account and run the CloudFormation deploy command with each user's access keys from a script.

<details><summary>Answer</summary>

**Answer: A.** Self-managed permissions exist for exactly this case: they establish the trust with two IAM roles rather than through organization membership, so a stack set can deploy to any account where the required execution role exists. The execution role must carry the default name to be used automatically, and it must trust the administrator account. B is not possible, because service-managed permissions require the targets to be accounts in the administrator's own organization with all features enabled. C solves the technical problem by changing the business relationship, giving the provider governance control over customer accounts that customers are unlikely to grant, and is not a deployment mechanism. D replaces temporary credentials with long-term access keys in 30 accounts and rebuilds the coordination, failure tolerance and reporting a stack set already provides.

*Where this is covered: StackSets across accounts and Regions.*

</details>

### 6. Sharing a subnet between two stacks (Associate)

A network team maintains a CloudFormation stack that creates a VPC and its subnets in one account and Region. Several application teams deploy their own stacks and need the subnet IDs. The company wants the sharing mechanism to make it impossible to delete the network stack while an application stack is still using its subnets.

Which solution will meet these requirements?

- **A)** Convert the application stacks into nested stacks of the network stack.
- **B)** Publish the subnet IDs to Parameter Store and read them with a dynamic reference in each application stack.
- **C)** Add `Export` names to the subnet outputs of the network stack and use `Fn::ImportValue` in the application stacks.
- **D)** Use `Fn::GetStackOutput` in the application stacks to read the network stack's outputs.

<details><summary>Answer</summary>

**Answer: C.** An exported output plus `Fn::ImportValue` creates a strong reference: after another stack imports the value, AWS documents that you cannot delete the exporting stack or modify the exported value until every import is removed, which is precisely the protection the company asked for. A would put the application stacks under the network stack's lifecycle and force every application deployment to run from the network root stack, which is not what independent teams want. B resolves a value at deploy time with no record of who is using it, so the network stack could still be deleted. D is a weak reference by design: nothing blocks deletion of the referenced stack, which is the requirement being tested.

*Where this is covered: Nested stacks compared with cross-stack references.*

</details>

### 7. A stack operation that never finishes (Associate)

A stack includes a custom resource backed by an AWS Lambda function that registers a domain name with an internal system. During a recent deployment the function raised an unhandled exception after a few seconds, and the stack remained in `CREATE_IN_PROGRESS` for an hour before failing. The team needs the stack to fail quickly when the function has a problem.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Modify the function so that it catches its own errors and uploads a response with a `Status` of `FAILED` to the pre-signed URL supplied in the request.
- **B)** Reduce the Lambda function timeout so that CloudFormation is notified when the function stops.
- **C)** Set the `ServiceTimeout` property on the custom resource to a value close to the expected response time.
- **D)** Add a `DependsOn` attribute so the custom resource is created last.
- **E)** Replace the custom resource with an `AWS::CloudFormation::WaitCondition` resource.

<details><summary>Answer</summary>

**Answer: A and C.** CloudFormation waits for the provider to upload a response to the pre-signed Amazon S3 URL, and a failed response or no response at all fails the operation, so the function must report its own failure rather than crashing silently. Lowering `ServiceTimeout` from the 3600-second default caps how long CloudFormation waits when the response never arrives. B does not help, because a Lambda timeout is not communicated to CloudFormation; the function simply stops without posting a response, which is the original problem. D changes provisioning order and has no effect on the hang. E replaces one mechanism that waits for an external signal with another that also waits for an external signal, and provides none of the custom provisioning logic.

*Where this is covered: Extending CloudFormation: custom resources, macros, Hooks and the registry.*

</details>

### 8. Limiting the blast radius of a StackSet update (Professional)

A platform team manages a service-managed StackSet that deploys a security baseline to 90 accounts across four Regions. A previous update contained an error and failed in most accounts before anyone noticed. The team wants future updates to stop after affecting as few accounts as possible, and to fail first in an account and Region where the damage is smallest.

Which solution will meet these requirements?

- **A)** Set a low failure tolerance per Region, a low maximum concurrent accounts value, and sequential Region concurrency with a test Region first in the deployment order.
- **B)** Set Region concurrency to parallel so that all Regions complete at once and failures are visible sooner.
- **C)** Enable termination protection on every stack instance.
- **D)** Run drift detection on the StackSet immediately after each update.

<details><summary>Answer</summary>

**Answer: A.** Failure tolerance is evaluated per Region, so a low value stops the operation as soon as a small number of accounts fail, the maximum concurrent accounts value limits how many are touched before that threshold is reached, and sequential Region concurrency with the test Region first means the failure happens where it does least harm. B does the opposite of what is needed, pushing the bad change to every Region at once. C prevents stack deletion and has no effect on updates. D reports unmanaged changes after the fact and neither stops nor reverses a bad update. Note that rollback triggers are not available here: they are a parameter of individual stack operations, not of a stack set operation.

*Where this is covered: StackSets across accounts and Regions.*

</details>

### 9. Finding out who changed what (Associate)

An audit shows that the security group rules on a production instance differ from what the team believes was deployed. The team must determine, for a specific CloudFormation stack, which resources no longer match the configuration in the stack's template and what the differences are.

Which solution will meet these requirements?

- **A)** Create a change set from the current template and review the proposed changes.
- **B)** Run drift detection on the stack and review the resource drift results.
- **C)** Review the stack events for the most recent update operation.
- **D)** Compare the template in the repository with the template returned by `get-template`.

<details><summary>Answer</summary>

**Answer: B.** Drift detection compares each supported resource's actual property values with the expected values from the template and parameters, and reports the differing properties with expected and actual values. A compares a proposed template with the stack's recorded configuration, which says nothing about changes made outside CloudFormation. C shows what CloudFormation itself did, and a manual change made in another console never appears there. D compares two templates with each other, not either of them with reality.

*Where this is covered: Drift detection, resource import and the IaC generator.*

</details>

### 10. Adopting an acquired environment (Professional)

A company acquires a business whose production application runs in a separate AWS account and was built entirely through the console. The application must not experience downtime. The company must bring the existing resources under CloudFormation management, keep the templates in its source repository, and be able to redeploy the same architecture into a second Region later.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Run an IaC generator resource scan in the account, select the application's resources and their related resources, and generate a template.
- **B)** Write a new template from scratch, deploy it as a new stack, migrate the data, and delete the original resources.
- **C)** Enable drift detection on the account so CloudFormation begins managing the resources it finds.
- **D)** Import the resources into a CloudFormation stack using the generated template, then commit the template to the repository.
- **E)** Create a StackSet that targets the acquired account so the existing resources are adopted automatically.

<details><summary>Answer</summary>

**Answer: A and D.** The IaC generator scans resources that CloudFormation does not already manage and writes a template describing them, and an import operation then brings those existing resources into a stack without creating or recreating anything, which satisfies the no-downtime requirement. Once the stack exists, the template is an ordinary artifact that can be committed and deployed elsewhere. B meets the management requirement but explicitly causes the downtime the scenario forbids. C misstates what drift detection does: it compares managed resources with their template and never adopts anything. E also misstates a mechanism, because a stack set creates new stacks in target accounts rather than adopting resources that already exist.

*Where this is covered: Drift detection, resource import and the IaC generator.*

</details>

## Summary

CloudFormation is a sequence of decisions about a template and the machinery around it. Decide what goes in one stack, remembering the 500-resource ceiling, and whether the pieces share a lifecycle, which chooses nested stacks, or are shared long-lived infrastructure, which chooses exported outputs and `Fn::ImportValue` with the deletion lock that comes with them. Decide how a change is reviewed: a change set before execution, or a Git sync pull request comment, and whether the update forces replacement of anything that holds data. Decide what protects the resources you cannot lose: a stack policy as the update fail-safe, `DeletionPolicy` for stack deletion, `UpdateReplacePolicy` for replacement, termination protection for the stack itself, and a service role so CloudFormation can do less than its operator. Decide how a failure behaves: roll back, preserve successfully provisioned resources and retry, or roll back automatically on a CloudWatch alarm. Decide the scope: one stack, or a StackSet with self-managed roles for accounts you do not govern and service-managed permissions with automatic deployment for organizational units you do. Then close the loop with drift detection for changes made by hand, and the IaC generator with resource import for infrastructure that was never in a template.

## Related units

- [AWS Service Catalog](service-catalog.md): publishing approved CloudFormation templates as products with launch constraints
- [AWS Elastic Beanstalk](../02-compute/elastic-beanstalk.md): the managed application platform that provisions a conventional application stack for you
- [Developer tools and CI/CD](developer-tools-and-cicd.md): pipelines that create and execute change sets as a deployment stage
- [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md): trusted access, delegated administrators and the account structure StackSets deploy into
- [AWS Identity and Access Management](../07-security/iam.md): the service role, `iam:PassRole`, and the capability acknowledgement for IAM resources in templates
- [Detection and compliance services](../07-security/detection-and-compliance-services.md): AWS Config for continuous configuration monitoring alongside point-in-time drift detection
- [AWS Systems Manager](systems-manager.md): Parameter Store values consumed by templates, and automation for what CloudFormation does not provision
- [The AWS API, CLI and SDKs](aws-api-cli-and-sdks.md): the CLI and SDKs for one-off and scripted calls rather than managed infrastructure

## Sources

- [CloudFormation template sections](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html): the ten top-level sections and which one is required
- [CloudFormation template Parameters syntax](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html): parameter types, constraints, and what `NoEcho` does and does not mask
- [Intrinsic function reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/intrinsic-function-reference.html): the full function list and where functions may be used
- [Get AWS values using pseudo parameters](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/pseudo-parameter-reference.html): every pseudo parameter and what it returns
- [Understand CloudFormation quotas](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html): resources, parameters, mappings, outputs, template body sizes, stacks, stack sets, stack instances, Hooks and modules
- [Update CloudFormation stacks using change sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html): the change set workflow and what pre-deployment validation does and does not guarantee
- [Understand update behaviors of stack resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html): no interruption, some interruption and replacement, and the nested stack note
- [Choose how to handle failures when provisioning resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stack-failure-options.html): preserve successfully provisioned resources, retry, update and roll back
- [Continue rolling back an update](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html): `UPDATE_ROLLBACK_FAILED` and skipping resources to finish a rollback
- [Roll back your CloudFormation stack on alarm breach with rollback triggers](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-rollback-triggers.html): five triggers, 0 to 180 minute monitoring time and the missing-data behavior
- [CreateStack](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_CreateStack.html): `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_AUTO_EXPAND`, `OnFailure` and template size limits
- [Prevent updates to stack resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html): stack policy syntax, the update actions, the `NotResource` warning and the override policy
- [Protect CloudFormation stacks from being deleted](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-protect-stacks.html): termination protection, nested stack behavior and how it differs from disabling rollback
- [CloudFormation service role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html): what a service role changes, `iam:PassRole` and why it cannot be removed
- [`DeletionPolicy` attribute](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-deletionpolicy.html): Delete, Retain, RetainExceptOnCreate, Snapshot and the RDS default
- [`UpdateReplacePolicy` attribute](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-updatereplacepolicy.html): when it fires and how it differs from `DeletionPolicy`
- [Split a template into reusable pieces using nested stacks](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-nested-stacks.html): root and parent stacks, `package`, and updating from the root
- [`Fn::GetStackOutput`](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/intrinsic-function-reference-getstackoutput.html): cross-account and cross-Region references, the `RoleArn` requirement, the weak reference note and the current limitations
- [Get exported outputs from a deployed CloudFormation stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-exports.html): the export restrictions and the comparison with `Fn::GetStackOutput`
- [StackSets concepts](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-concepts.html): stack instances, permission models, operation preferences and status codes
- [Grant self-managed permissions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html): the administration and execution role names and their trust policies
- [Activate trusted access for StackSets with AWS Organizations](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-activate-trusted-access.html): the all-features requirement and the service-linked roles created
- [Enable or disable automatic deployments for StackSets in AWS Organizations](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-manage-auto-deployment.html): what happens on account add, move and removal
- [Detect unmanaged configuration changes to stacks and resources with drift detection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html): drift statuses and every documented limitation
- [Performing drift detection on CloudFormation StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-drift.html): how stack set drift rolls up from stack instances
- [Import AWS resources into a CloudFormation stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import.html): resource import, auto-import and stack refactoring
- [Generate templates from existing resources with IaC generator](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/generate-IaC.html): the scan, its 30-day life, the quotas and the Cloud Control API constraint
- [Create custom provisioning logic with custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html): the request and response protocol and the 3600-second default timeout
- [Perform custom processing on CloudFormation templates with template macros](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html): hosted transforms, custom macros and billing
- [What are CloudFormation Hooks?](https://docs.aws.amazon.com/cloudformation-cli/latest/hooks-userguide/what-is-cloudformation-hooks.html): the four implementation options and fail or warn behavior
- [Managing extensions with the CloudFormation registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html): public and private extensions and how registry resources differ from custom resources
- [Create reusable resource configurations with CloudFormation modules](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/modules.html): module processing and the quota considerations
- [Syncing stacks with source code stored in a Git repository with Git sync](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/git-sync.html): the deployment file, supported providers and pull request comments
- [AWS CloudFormation pricing](https://aws.amazon.com/cloudformation/pricing/): free for AWS resource types, per handler operation for third-party extensions and custom Hooks
