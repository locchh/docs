# S3 Additional Checksums

## Objective

Learn how to use and configure additional checksums when uploading objects to Amazon S3, ensuring data integrity with custom checksum algorithms.

## Prerequisites

1. AWS CLI installed and configured on your environment.
2. Basic knowledge of Linux command line.
3. Familiarity with file handling and checksum commands.

## 1. Create an S3 Bucket

- Use the AWS CLI to create a bucket:

```bash
aws s3 mb s3://checksums-examples-ab123
```

- Verify that the bucket was created successfully:

```bash
aws s3 ls
```

## 2. Create a File

Generate a simple file to work with:

```bash
echo "Hello Mars" > myfile.txt
```

## 3. Generate an MD5 Checksum

Use the `md5sum` command to calculate the MD5 checksum of the file:

```bash
md5sum myfile.txt
```

Note the generated checksum for comparison.

## 4. Generate a Custom Checksum

To use a checksum algorithm supported by S3 for validation (SHA-256, SHA-1, CRC32, CRC32C). Compute the checksum using openssl (for SHA-1):

```bash
CHECKSUM_SHA1=$(openssl dgst -sha1 -binary myfile.txt | base64)
```

Replace `-sha1` with `-sha256` for SHA-256.

## 5. Upload File with Custom Checksum

Use the `aws s3api put-object` command, specifying the checksum algorithm and the pre-computed checksum value:

```bash
aws s3api put-object \
       --bucket="checksums-examples-ab123" \
       --key="myfilesha1.txt" \
       --body="myfile.txt" \
       --checksum-algorithm="SHA1" \
       --checksum-sha1="$CHECKSUM_SHA1" \
       --metadata ChecksumSHA1="$CHECKSUM_SHA1"
```

- The `--checksum-sha1` flag provides the checksum value.
- The `--metadata` flag adds a custom metadata tag (`x-amz-meta-checksumsha1`) to the object.

Verify the upload. Use the AWS CLI to check the object:

```bash
aws s3api head-object \
--bucket checksums-examples-ab123 \
--key myfilesha1.txt
```

Use the AWS Management Console to confirm that the **Checksum** and Metadata sections include the SHA-1 value.

## 6. Tips for Troubleshooting

**Common Error**: "An error occurred (InvalidRequest) when calling the PutObject operation: Value for x-amz-checksum-sha1 header is invalid."

**Cause**: Missing or incorrectly formatted checksum value.

**Solution:**

- Ensure the checksum is Base64 encoded.
- Use the correct algorithm (SHA-256, SHA-1, CRC32, CRC32C).
- Include the corresponding `x-amz-checksum-*algorithm*` header in your API call.
- Example for SHA-1:

```bash
CHECKSUM_SHA1=$(openssl dgst -sha1 -binary myfile.txt | base64)

aws s3api put-object \
    --bucket="checksums-examples-ab123" \
    --key="myfilesha1.txt" \
    --body="myfile.txt" \
    --checksum-algorithm="SHA1" \
    --checksum-sha1="$CHECKSUM_SHA1" \
    --metadata ChecksumSHA1="$CHECKSUM_SHA1"
```

**Outcome**

You now understand how to:

1. Generate custom checksums using supported algorithms.
2. Upload files to S3 with pre-computed checksums.
3. Troubleshoot common issues with checksum validation.
