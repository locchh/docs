# Machine learning and media

Neither Solutions Architect exam asks you to train a model. It asks whether you
recognize that AWS already sells the capability a scenario describes, so you do
not design a custom build. **Amazon Rekognition** analyzes images and video,
**Amazon Textract** extracts text and structure from documents, **Amazon
Transcribe** turns speech into text, **Amazon Comprehend** finds entities and
sentiment in text, **Amazon Translate** converts between languages, **Amazon
Polly** turns text into speech, and **Amazon SageMaker AI** is the platform for
the cases where a custom model really is needed. The media and device units
cover the same idea for video processing, device testing and connected hardware.

The decision the category keeps asking you to make is whether a managed API
already answers the requirement before anything gets built. The exam signals
this with plain descriptions rather than service names: "extract values from
scanned invoices" is Textract, not Rekognition and not a custom function with a
library in it. Learning the wording-to-service mapping is most of the work, and
the first unit exists mainly to carry that table.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [ml-managed-services.md](ml-managed-services.md) | Map a described capability to the right managed service, and place SageMaker AI endpoints when one is needed | M |
| [ai-dev-tools-and-generative-ai.md](ai-dev-tools-and-generative-ai.md) | Recognize the generative AI services and the controls a question about them is really testing | S |
| [media-iot-and-device-farm.md](media-iot-and-device-farm.md) | Place video processing, device testing and connected-device workloads on the right service | XS group |

## Which exam tasks this serves

On SAA-C03 it is task 2.2, which names Amazon Comprehend and Amazon Polly as
managed services with appropriate use cases, and task 2.1, which asks you to use
purpose-built AWS services for workloads. On SAP-C02 it is task 2.5, the
methodology for selecting purpose-built services, task 3.3 for proposing new
managed technologies, plus the emerging-topics area
on security and responsible AI controls, which names Guardrails in **Amazon
Bedrock**, the managed foundation model service, AgentCore Identity, and human
approval workflows built on **AWS Step Functions**, the managed workflow
service.

## Reading order

Read `ml-managed-services.md` and study its comparison table until you can go
from a described capability to a service without hesitating; that is the only
part of this category that reliably appears on SAA-C03. Read
`ai-dev-tools-and-generative-ai.md` next, noting that Bedrock is on neither
exam's in-scope list, so a question naming it is testing the architecture around
it. An Associate-only candidate can skim `media-iot-and-device-farm.md`: the
**AWS IoT** family, for connected devices, is in scope for SAP-C02 only, and the
**AWS Elemental** media services are named on the SAA-C03 out-of-scope list.
**Amazon Kendra**, enterprise search, **Amazon Personalize**, recommendations,
and **Amazon Fraud Detector**, fraud scoring, in the first unit are
Professional-only too, and Personalize is named on the SAA-C03 out-of-scope
list.
