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

module "python_veryfy_pin_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "verify-pin"
  function_entry_point = "verify_pin"
  sourcefn             = "python-function-verify-pin"
  runtimefn              = "python310"
}
module "python_account_management_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "account-management"
  function_entry_point = "account_management"
  sourcefn             = "python-account-management"
  runtimefn              = "python310"
}

module "python_get_speaker_ids_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "get-speaker-ids"
  function_entry_point = "get_speaker_ids"
  sourcefn             = "python-get-speaker-ids"
  runtimefn              = "python310"
}
module "python_register_speaker_ids_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "register-speaker-id"
  function_entry_point = "register_speaker_id"
  sourcefn             = "python-register-speaker-id"
  runtimefn              = "python310"
}

module "python-cepf-lab" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "cepf-lab-wh"
  function_entry_point = "main"
  sourcefn             = "python-cepf-lab"
  runtimefn              = "python310"
}
module "v2-node-stt" {
  source               = "./modules/functionsv2"
  project              = var.project
  function_name        = "v2-stt-recognize"
  function_entry_point = "index"
  sourcefn             = "v2-node-stt"
  runtimefn            = "nodejs16"
  location             = "us-central1"
}

module "v2-node-main" {
  source               = "./modules/functionsv2"
  project              = var.project
  function_name        = "v2-testing"
  function_entry_point = "index"
  sourcefn             = "v2-node-sample"
  runtimefn             = "nodejs16"
  location             = "us-central1"
}

     
module "secrets" {
  source               = "./modules/secrets"
  project              = var.project
}
