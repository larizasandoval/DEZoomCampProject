variable "project_id" {
  description = "Project for data zoomcap project"
  default     = "project-0f0167b9-0302-4715-840"
}

variable "region" {
  description = "GCP region"
  default     = "us-central1"
}

variable "gcs_bucket_name" {
  description = "bucke name"
  default     = "science_production_data_lake"
}

variable "bq_dataset_id" {
  description = "Data id in BigQuery"
  default     = "science_p_raw_data"
}