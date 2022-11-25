provider "google" {
  project = var.project
  region  = var.region
}
## Adding secrets for Salesforce Authentication

## Enable API

module "python_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "salesforce-connector-wh"
  function_entry_point = "main"
  sourcefn             = "python-function-salesforce"
  runtimefn              = "python310"
}

module "node_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "dialogflow-main-wh"
  function_entry_point = "hospitalityMainWH"
  sourcefn             = "node-function-sample"
  runtimefn              = "nodejs16"
}

 module "node_main_feature_testing" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "feature-testing-node"
  function_entry_point = "main"
  sourcefn             = "feature-testing"
  runtimefn              = "nodejs16"
}


     
module "secrets" {
  source               = "./modules/secrets"
  project              = var.project
}
