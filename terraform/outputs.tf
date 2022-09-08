output "function_uri_dialog_main" {
	value = module.node_function_main
}

output "function_uri_salesforce" {
	value = module.python_function_main.function_url
}
