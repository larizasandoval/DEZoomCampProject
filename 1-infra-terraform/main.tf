terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}


# Crear el Bucket (Data Lake) para guardar los archivos anuales de la encuesta
resource "google_storage_bucket" "data-lake" {
  name          = "${var.gcs_bucket_name}"
  location      = var.region
  force_destroy = true # Permite borrar el bucket aunque tenga datos (útil para el proyecto)
  storage_class = "STANDARD"
  uniform_bucket_level_access = true
}

# Crear el Dataset de BigQuery (Data Warehouse)
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_id
  location   = var.region
}