from heliostat.workarounds.wsgi import WSGIShim


class TestWSGIShim:
    def test_apply_adds_wsgi_shim_part(self):
        yaml = {"name": "test", "parts": {"existing": {"plugin": "nil"}}}
        WSGIShim(module="nova.wsgi", script_name="nova-api").apply(yaml)
        assert "wsgi_shim" in yaml["parts"]

    def test_apply_part_uses_dump_plugin(self):
        yaml = {"name": "test", "parts": {}}
        WSGIShim(module="nova.wsgi", script_name="nova-api").apply(yaml)
        assert yaml["parts"]["wsgi_shim"]["plugin"] == "dump"

    def test_apply_organizes_script_to_usr_bin(self):
        yaml = {"name": "test", "parts": {}}
        WSGIShim(module="nova.wsgi", script_name="nova-api").apply(yaml)
        assert yaml["parts"]["wsgi_shim"]["organize"] == {
            "nova-api": "usr/bin/"
        }

    def test_apply_does_not_modify_existing_parts(self):
        yaml = {"name": "test", "parts": {"existing": {"plugin": "nil"}}}
        WSGIShim(module="nova.wsgi", script_name="nova-api").apply(yaml)
        assert "existing" in yaml["parts"]

    def test_script_contains_correct_import(self):
        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        assert "from nova.wsgi import application" in shim.script()

    def test_pre_build_writes_script_file(self, tmp_path):
        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        shim.pre_build(tmp_path)
        script_file = tmp_path / "nova-api"
        assert script_file.exists()
        assert "from nova.wsgi import application" in script_file.read_text()

    def test_pre_build_script_name_matches_field(self, tmp_path):
        shim = WSGIShim(module="heat.wsgi", script_name="heat-api")
        shim.pre_build(tmp_path)
        assert (tmp_path / "heat-api").exists()
