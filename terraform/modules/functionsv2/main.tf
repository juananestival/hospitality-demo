# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions_function
locals {
  timestamp = formatdate("YYMMDDhhmmss", timestamp())
	root_dir = abspath("../src/${var.sourcefn}")
}
# Compress source code
data "archive_file" "source" {
  type        = "zip"
  source_dir  = local.root_dir
  output_path = "/tmp/function-${var.sourcefn}-${local.timestamp}.zip"
}

# Create bucket that will host the source code
resource "google_storage_bucket" "bucket" {
  name = "${var.project}-${var.sourcefn}-function"
  location = "US"
  uniform_bucket_level_access = true
}

# Add source code zip to bucket
resource "google_storage_bucket_object" "zip" {
  # Append file MD5 to force bucket to be recreated
  name   = "source.zip#${data.archive_file.source.output_md5}"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

# Enable Cloud Functions API
resource "google_project_service" "cf" {
  project = var.project
  service = "cloudfunctions.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
}

# Enable Cloud Build API
resource "google_project_service" "cb" {
  project = var.project
  service = "cloudbuild.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
}

# Create Main tree Cloud Function
resource "google_cloudfunctions2_function" "function" {
  name    = var.function_name
  location    = var.location
  description = "a new function"
  build_config {
    runtime = var.runtimefn
    entry_point = var.function_entry_point  # Set the entry point 
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.zip.name
      }
    }
  }
  service_config {
    max_instance_count  = 10
    available_memory    = "256M"
    timeout_seconds     = 3000
  }

}


# Create IAM entry so all users can invoke the function
resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project = google_cloudfunctions2_function.function.project
  location = var.location 

  #region         = google_cloudfunctions2_function.function.region
  cloud_function = google_cloudfunctions2_function.function.name
  role   = "roles/cloudfunctions.invoker"
  member = "user:owner@estival.altostrat.com"
}
#output "function_uri" {
#  value = google_cloudfunctions2_function.function.service_config[0].uri
#}

#output "function_url" {
#  value = google_cloudfunctions2_function.function.https_trigger_url
#}