# AWS S3 Bash Scripting

## Prerequisites

- AWS CLI installed and configured
- GitPod or similar environment with Bash support
- JQ installed (`sudo apt-get install jq`)
- Basic understanding of Bash scripting

## Step 1: Set Up Environment

Read this. https://github.com/ExamProCo/AWS-Examples/tree/main/s3/bash-scripts

Create Directories:

```bash
mkdir -p S3/bash-scripts
cd S3/bash-scripts
```

Make Scripts Executable:

```bash
chmod +x *.sh
```

## Step 2: Create and Delete Buckets

Create Bucket Script (create_bucket.sh)

```bash
#!/bin/bash
set -e
if [ -z "$1" ]; then
    echo "No bucket name provided. Usage: $0 bucket-name"
    exit 1
fi
BUCKET_NAME=$1
REGION=${2:-us-east-1}
aws s3api create-bucket --bucket "$BUCKET_NAME" --create-bucket-configuration LocationConstraint="$REGION"
```

Delete Bucket Script (delete_bucket.sh)

```bash
#!/bin/bash
#!/bin/bash
set -e
if [ -z "$1" ]; then
    echo "No bucket name provided. Usage: $0 bucket-name"
    exit 1
fi
BUCKET_NAME=$1
aws s3api delete-bucket --bucket "$BUCKET_NAME"
```

## Step 3: Sync Files to Bucket

Generate Random Files Script (generate_files.sh):

```bash
#!/bin/bash
set -e
OUTPUT_DIR="./temp"
mkdir -p $OUTPUT_DIR
rm -rf $OUTPUT_DIR/*
NUM_FILES=$((RANDOM % 6 + 5))
for i in $(seq 1 $NUM_FILES); do
    FILE_NAME="$OUTPUT_DIR/file_$i.txt"
    head -c 100 </dev/urandom > $FILE_NAME
    echo "Created $FILE_NAME"
done
```

Sync Files Script (sync_files.sh)

```bash
#!/bin/bash
set -e
if [ -z "$1" ]; then
    echo "No bucket name provided. Usage: $0 bucket-name"
    exit 1
fi
BUCKET_NAME=$1
FILE_PREFIX=${2:-files}
aws s3 sync ./temp s3://$BUCKET_NAME/$FILE_PREFIX
```

## Step 4: List and Delete Objects

List Objects Script (list_objects.sh)

```bash
#!/bin/bash
set -e
if [ -z "$1" ]; then
    echo "No bucket name provided. Usage: $0 bucket-name"
    exit 1
fi
BUCKET_NAME=$1
aws s3api list-objects --bucket "$BUCKET_NAME" --query 'Contents[].{Key: Key, Size: Size}'
```

Delete All Objects Script (delete_objects.sh)

```bash
#!/bin/bash
set -e
if [ -z "$1" ]; then
    echo "No bucket name provided. Usage: $0 bucket-name"
    exit 1
fi
BUCKET_NAME=$1
OBJECTS=$(aws s3api list-objects --bucket "$BUCKET_NAME" --query 'Contents[].{Key: Key}' --output json)
if [ "$OBJECTS" == "null" ]; then
    echo "Bucket is empty"
    exit 0
fi
echo '{"Objects":' > delete.json
echo $OBJECTS | jq '.' >> delete.json
echo '}' >> delete.json
aws s3api delete-objects --bucket "$BUCKET_NAME" --delete file://delete.json
rm delete.json
```

## Step 5: Additional Utility Scripts

Get Newest Bucket Script (getnewestbucket.sh)

```bash
#!/bin/bash
aws s3api list-buckets --query 'Buckets | sort_by(@, &CreationDate) | [-1:].Name' --output text
```

List Buckets Script (list_buckets.sh)

```bash
#!/bin/bash
aws s3 ls
```

## Step 6: Running the Scripts

```bash
#  Generate Random Files
./generate_files.sh

#  Create a New Bucket
./create_bucket.sh my-new-bucket us-east-1

#  Sync Files to Bucket
./sync_files.sh my-new-bucket files

#  List Objects in Bucket
./list_objects.sh my-new-bucket

#  Delete All Objects in Bucket
./delete_objects.sh my-new-bucket

#  Delete the Bucket
./delete_bucket.sh my-new-bucket
```