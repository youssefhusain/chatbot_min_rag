import sys
import types


fake_controllers = types.ModuleType("controllers")

class FakeDataController:
    def validate_uploaded_file(self, file):
        return True, "OK"
    def generate_unique_filepath(self, orig_file_name, project_id):
        return f"/tmp/{orig_file_name}", "fake_file_id"

class FakeProjectController:
    def get_project_path(self, project_id):
        return "/tmp"

fake_controllers.DataController = FakeDataController
fake_controllers.ProjectController = FakeProjectController

sys.modules["controllers"] = fake_controllers
