resource "google_project_service" "secretmanager" {
  provider = google-beta
  service  = "secretmanager.googleapis.com"
  project = var.project
}

resource "google_secret_manager_secret" "user" {
  provider = google-beta
  project = var.project
  secret_id = "SF_USER_PROD"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret" "token" {
  provider = google-beta
  project = var.project
  secret_id = "SF_TOKEN_PROD"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret" "password" {
  provider = google-beta
  project = var.project
  secret_id = "SF_PASS_PROD"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.secretmanager]
}




