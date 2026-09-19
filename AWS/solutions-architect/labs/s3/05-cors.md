# Amazon S3 CORS Follow Along Lab

## Objective

Configure CORS (Cross-Origin Resource Sharing) for:

- An S3 static website
- An API Gateway endpoint

Demonstrate a CORS error and fix it by applying the correct policies.

---

## Step 1: Create S3 Static Website (Frontend)

### 1.1 Create S3 Bucket

```bash
aws s3api create-bucket \
  --bucket <your-bucket-name> \
  --region ca-central-1 \
  --create-bucket-configuration LocationConstraint=ca-central-1
```

### 1.2 Disable Block Public Access (Required)

```bash
aws s3api put-public-access-block \
  --bucket <your-bucket-name> \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

### 1.3 Add Bucket Policy (Public Read)

Create `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<your-bucket-name>/*"
    }
  ]
}
```

Apply policy:

```bash
aws s3api put-bucket-policy \
  --bucket <your-bucket-name> \
  --policy file://bucket-policy.json
```

### 1.4 Enable Static Website Hosting

Create `website.json`:

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

Apply:

```bash
aws s3api put-bucket-website \
  --bucket <your-bucket-name> \
  --website-configuration file://website.json
```

### 1.5 Upload index.html

```bash
aws s3 cp index.html s3://<your-bucket-name>/
```

### 1.6 Access Website

Format:

```
http://<bucket-name>.s3-website.ca-central-1.amazonaws.com
```

---

## Step 2: Create Second Bucket (Cross-Origin Resource)

### 2.1 Create Second Bucket

Repeat steps above with a new name:

```
<your-bucket-name>-2
```

### 2.2 Upload JS File

Create `hello.js`:

```javascript
console.log("Hello from another origin");
```

Upload:

```bash
aws s3 cp hello.js s3://<bucket-name-2>/
```

### 2.3 Reference Cross-Origin Script

Update `index.html`:

```html
<script src="http://<bucket-2>.s3-website.ca-central-1.amazonaws.com/hello.js"></script>
```

At this point:

- It may still work
- Not all cross-origin requests trigger CORS (GET is often allowed)

---

## Step 3: Force a CORS Error (API Gateway)

### 3.1 Create API Gateway (REST API)

- Go to API Gateway
- Create REST API
- Create resource: `/hello`
- Add method: **POST**
- Set integration type: **Mock**

### 3.2 Configure Mock Response

In Integration Response → Mapping Templates:

```json
{
  "message": "hello world"
}
```

### 3.3 Deploy API

- Create stage: `prod`
- Copy invoke URL:

```
https://<api-id>.execute-api.ca-central-1.amazonaws.com/prod/hello
```

### 3.4 Test with curl

```bash
curl -X POST \
  https://<api-id>.execute-api.ca-central-1.amazonaws.com/prod/hello \
  -H "Content-Type: application/json"
```

### 3.5 Call API from index.html

Add JavaScript:

```html
<script>
const xhr = new XMLHttpRequest();
xhr.open("POST", "https://<api-id>.execute-api.ca-central-1.amazonaws.com/prod/hello");
xhr.setRequestHeader("Content-Type", "application/json");

xhr.onreadystatechange = function () {
  if (xhr.readyState === 4 && xhr.status === 200) {
    const result = JSON.parse(xhr.responseText);
    console.log(result);
  }
};

xhr.send();
</script>
```

**Result: CORS Error**

In browser DevTools:

```
Access to XMLHttpRequest has been blocked by CORS policy
```

---

## Step 4: Fix CORS

### 4.1 Add CORS Policy to S3

Create `cors.json`:

```json
[
  {
    "AllowedOrigins": ["http://<your-bucket-name>.s3-website.ca-central-1.amazonaws.com"],
    "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
    "AllowedHeaders": ["*"]
  }
]
```

Apply:

```bash
aws s3api put-bucket-cors \
  --bucket <your-bucket-name> \
  --cors-configuration file://cors.json
```

### 4.2 Enable CORS in API Gateway

- Go to API Gateway → Resource
- Click **Enable CORS**
- Configure:
  - Access-Control-Allow-Origin: `*` (or your S3 URL)
  - Methods: POST
- Save

### 4.3 Redeploy API

> **Important**: Changes do NOT apply until you redeploy

### 4.4 Test Again

- Hard refresh browser (disable cache)
- Open DevTools → Network

**Result:**

- Request succeeds
- JSON response returned
- No CORS error

---

## Key Takeaways (Exam + Real World)

### When CORS Happens

- Triggered by:
  - Different origin (domain, protocol, or port)
  - Especially POST, PUT, DELETE
- Browser sends a preflight (OPTIONS) request

### CORS Must Be Enabled on:

- **Client resource (S3)** → allows origin
- **Server resource (API Gateway)** → returns headers

### Required Headers

- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

### Common Pitfalls

- Forgetting to redeploy API Gateway
- Using wrong origin format (http vs https)
- Not handling preflight request
- Caching hiding changes

---

## Cleanup

### Delete API Gateway

- Delete stage
- Delete API

### Delete Buckets

```bash
aws s3 rm s3://<bucket-name> --recursive
aws s3 rb s3://<bucket-name>
```
