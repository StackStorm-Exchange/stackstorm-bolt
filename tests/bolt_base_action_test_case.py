import yaml
import json

from st2tests.base import BaseActionTestCase


class BoltBaseActionTestCase(BaseActionTestCase):
    __test__ = False

    def setUp(self):
        super(BoltBaseActionTestCase, self).setUp()

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))
