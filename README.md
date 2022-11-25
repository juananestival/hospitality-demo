# hospitality-demo

```sh
terraform apply -target=module.python_function_main --auto-approve
terraform apply -target=module.node_function_main --auto-approve
terraform apply -target=module.node_main_feature_testing --auto-approve
```

Python env creation
```sh
python3 -m venv venv
```

Python env activation
```sh
source venv/bin/activate
```
Python env installation
```sh
pip install functions-framework
```

pip install -r requirements.txt


https://pypi.org/project/simple-salesforce/

Note if you copy past the number in Dialog Flow console then a unicode character si addad 202 for the copy paste and the query don'tm work

## Created localtesting to test the python functions before upload them
I'll create a branch called localtesting

## The functions are created in the project.
this means that it should be accesible from any agent. 
 to add a new node funciton
 ```tf
 module "node_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "a-name"
  function_entry_point = "the value of the exports.hospitalityMainWH = (req, res) => {"
  sourcefn             = "the directory"
  runtimefn              = "nodejs16"
}
```