# Xmas Gift Exchange

## Description

This is a simple app that allows you to create a gift exchange for a group of
people. It is designed to be used for a secret Santa type of gift exchange. It
is not a full-featured app, but it does the job.

## Requirements

* Python >= 3.8
* AWS Account
* Friends / family to exchange gifts

## Setup

1. Clone the repository to your local machine.
2. Create a `participants.csv` file with the following format:
   ```
   name,house
   Alice,North
   Bob,South
   Charlie,North
   ```
2. Run `python3 xmas_exchange.py` to generate the gift exchange data.
3. Copy the `encrypted_assignments.json` file to the `lambda_package` directory.
4. Note the `encryption_key` in the `encrypted_assignments.json` file.
5. Zip the `lambda_package` directory.
6. Run the terraform script to create the AWS resources.
   1. Run `terraform init` to initialize the terraform state.
   2. Run `terraform apply` to create the resources.
7. Take the output from the terraform script and update `/gh-pages/app.js` with
   the `api_endpoint`.
8. Replace the `<h1>` tag in `/gh-pages/index.html` with the name of your
   exchange.
8. Push the changes to your forked repository.