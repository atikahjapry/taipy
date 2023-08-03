# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

import pytest

from src.taipy.core._version._version import _Version
from src.taipy.core._version._version_fs_repository import _VersionFSRepository
from src.taipy.core._version._version_sql_repository import _VersionSQLRepository
from src.taipy.core.exceptions import ModelNotFound


class TestVersionFSRepository:
    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_save_and_load(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(_version)

        obj = repository._load(_version.id)
        assert isinstance(obj, _Version)

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_exists(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(_version)

        assert repository._exists(_version.id)
        assert not repository._exists("not-existed-version")

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_load_all(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir
        for i in range(10):
            _version.id = f"_version_{i}"
            repository._save(_version)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_load_all_with_filters(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            _version.id = f"_version_{i}"
            _version.name = f"_version_{i}"
            repository._save(_version)
        objs = repository._load_all(filters=[{"id": "_version_2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_delete(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(_version)

        repository._delete(_version.id)

        with pytest.raises(ModelNotFound):
            repository._load(_version.id)

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_delete_all(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            _version.id = f"_version_{i}"
            repository._save(_version)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_delete_many(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            _version.id = f"_version_{i}"
            repository._save(_version)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_search(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            _version.id = f"_version_{i}"
            _version.name = f"_version_{i}"
            repository._save(_version)

        assert len(repository._load_all()) == 10

        objs = repository._search("id", "_version_2")
        assert len(objs) == 1
        assert isinstance(objs[0], _Version)

    @pytest.mark.parametrize("repo", [_VersionFSRepository, _VersionSQLRepository])
    def test_export(self, tmpdir, _version, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(_version)

        repository._export(_version.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _VersionFSRepository else os.path.join(tmpdir.strpath, "version")

        assert os.path.exists(os.path.join(dir_path, f"{_version.id}.json"))
