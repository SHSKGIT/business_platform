import os
import pkgutil

# Get the current package name
package_name = __name__

# Iterate through all modules in the package directory
for _, module_name, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)]):
    if not ispkg:
        # Import the module dynamically
        module = __import__(f"{package_name}.{module_name}", fromlist=[module_name])
        # Add the module to the package's globals
        globals()[module_name] = module
