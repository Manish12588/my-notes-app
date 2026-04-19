variable "aws_region" {
  description = "This varibles holds the value of AWS region"
  default     = "ap-south-1"

  validation {
    condition     = contains(["ap-south-1", "us-east-1", "us-west-2"], var.aws_region)
    error_message = "Region must be ap-south-1, us-east-1, or us-west-2."
  }
}

variable "instances" {
  description = "Map of instance name to AMI IDs, SSH User, and OS family."

  #Created a map to tell the type of all variables
  type = map(object({
    ami           = string
    user          = string
    os_family     = string
    instance_type = string
  }))

  default = {
    "my-notes-app-server" = {
      ami           = "ami-05d2d839d4f73aafb" #Ubuntu Server 24.04 LTS region: ap-south-1 
      user          = "ubuntu"
      os_family     = "Debian"
      instance_type = "t3.micro"
    }
  }
}
