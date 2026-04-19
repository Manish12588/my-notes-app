terraform {
  backend "s3" {
    bucket       = "my-notes-app-tfstate"
    key          = "prod/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true                      # ✅ replaces deprecated dynamodb_table
    encrypt      = true
  }
}