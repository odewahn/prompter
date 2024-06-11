from pymacapp.buildtools.app import App
from pymacapp.buildtools.package import Package
import os
import dotenv

# Load the environment variables
dotenv.load_dotenv()

APP_NAME = "prompter"
APP_PATH = "main.py"
IDENTIFIER = "com.odewahn.prompter"

# CREDENTIALS
APPLE_DEVELOPER_EMAIL = os.environ["APPLE_EMAIL"]
APPLE_DEVELOPER_TEAM_ID = os.environ["APPLE_DEVELOPER_TEAM_ID"]
APPLE_APP_SPECIFIC_PASSWORD = os.environ["APPLE_APP_SPECIFIC_PASSWORD"]
APP_HASH = App.get_first_hash()
PKG_HASH = Package.get_first_hash()

print(f"APP_HASH: {APP_HASH}")
print(f"PKG_HASH: {PKG_HASH}")

## APP

# create the app wrapper
app = App(APP_NAME)
app.config(APP_PATH).build().sign(APP_HASH)

## PACKAGE

# create the package wrapper
package = Package(app, identifier=IDENTIFIER)
# explicit authentication required starting in v.4.0.1
package.login(
    APPLE_DEVELOPER_EMAIL, APPLE_APP_SPECIFIC_PASSWORD, APPLE_DEVELOPER_TEAM_ID
)
# begin processing
package.build().sign(Package.get_first_hash()).notarize()
package.log_full_notary_log()
package.staple()
