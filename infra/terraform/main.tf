# Configuração Terraform para Infraestrutura do Cofre Digital (Exemplo AWS)

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# 1. VPC para isolamento de rede
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "cofre-vpc"
  cidr   = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}

# 2. Banco de Dados Gerenciado (RDS Postgres)
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  db_name              = "cofredigital"
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.t3.micro"
  username             = "admin_cofre"
  password             = var.db_password
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true
}

# 3. Cluster Kubernetes (EKS)
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "cofre-cluster"
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    main = {
      min_size     = 1
      max_size     = 3
      desired_size = 2
      instance_types = ["t3.medium"]
    }
  }
}

variable "db_password" {
  description = "Senha do banco de dados"
  type        = string
  sensitive   = true
}
